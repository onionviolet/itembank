# Phase 5: Check Item Type & Code Editor - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers four things and nothing else:

1. **A `check` item type** in the format contract — stem, learner-written code, and
   **multiple** authored test cases, parsed by `model.py` like every other type and
   documented in `SPEC`.
2. **A runner** that executes the learner's code out of process, with a timeout and a
   process-tree kill that works on Windows and POSIX, including grandchildren.
3. **A dichotomous verdict through `runtime.score_response()`** — the same one scorer,
   reached the same way, with no second grading path anywhere.
4. **A real code editor field** in the browser surface: monospace, working line
   numbers, and a tab key that inserts a tab instead of moving focus.

**Explicitly not in this phase:**

- **Any claim of sandboxing or isolation.** CODE-05 makes the absence of that claim a
  deliverable. This stops accidents, not deliberate escapes, and the documentation says
  so plainly (D-09).
- Runnable code inside lesson prose (LOOP-03, Phase 9). That reuses this runner; it is
  not built here.
- Model-marked or model-hinted code (Phase 8).
- Theming the editor (Phase 4).
- Any language beyond Python. D-02 makes a second language a config entry rather than a
  code change, and ships exactly one.

</domain>

<decisions>
## Implementation Decisions

**All decisions in this section were delegated by the user.** Asked which of four gray
areas to discuss, Weibao selected "Delegate all" — the standing instruction from
`02.1-CONTEXT.md`: *"the most optimal solution that gives us the most options and
directions in the future."* Every D-number is Claude's judgment resolved toward
optionality and reversibility. The planner may revise any of them with a stated reason.

### Where execution lives relative to the scorer

- **D-01:** **The runner runs before the scorer, never inside it.** `runtime.py`'s
  `canonical_response()` (line 70) and `canonical_key()` (line 103) are pure string
  reductions with three consumers, one of which is a static offline HTML page. Spawning
  a subprocess inside either of them would put process execution on a code path the
  browser shares and break the property that makes the offline page trustworthy.
  The shape instead:
  - A new `runner.py` (peer of `model.py` / `runtime.py`, importing neither surface nor
    server) executes the learner's source against each authored case and returns a
    **results vector** — one pass/fail per case, in authored order.
  - `canonical_response(q, answer)` for `check` reduces that vector to
    `"1,1,0"`-shaped text; `canonical_key(q)` is all-ones of the same length.
  - `score_response()` compares them, unchanged, and CODE-02's "through the same
    scorer" is structurally true rather than asserted.
  — **Reversibility:** costly — the alternative (execution inside the scorer) would
  need every existing caller of `canonical_response` audited for side effects, so
  getting this backwards is expensive to undo.
- **D-02:** Language is an **item field with a settings-driven allowlist**:
  `[LANG: python]` on the item, defaulting to `python`, validated against
  `check.languages`, a settings map of language → argv template. This phase ships
  exactly one entry (`python`, invoked as `sys.executable`), so C or JavaScript later is
  a configuration entry and not a fork of the runner — the same shape LOOP-05 asks for
  at subject level. A `[LANG:]` value absent from the allowlist is a lint error
  (`item.check_lang_unknown`), never a fallback.

### Format contract

- **D-03:** Test cases are authored as `CASE)` lines, matching the existing marker
  vocabulary exactly — `ROW)` for table, `ITEM)` for dnd, `STEP)` for build
  (`model.py:86-105`) — and reusing the same `::` split those rows already use:

  ```
  CASE) <stdin text> :: <expected stdout>
  ```

  Multiple `CASE)` lines mean multiple cases, which is what Success Criterion 2's "not
  one hardcoded string" requires. An item with fewer than two cases is a lint warning
  (`item.check_too_few_cases`), by the same reasoning `build` errors on fewer than two
  steps: one case tests almost nothing.
- **D-04:** `[MATCH: exact|trimmed|regex]` on the item, defaulting to `trimmed`
  (trailing-whitespace-and-newline tolerant). `trimmed` is the default because the
  overwhelmingly common CSCI 1100 failure is a missing or extra trailing newline, and
  failing a correct answer on that teaches nothing. `exact` and `regex` exist so a
  stricter item is authorable without a format change later.
- **D-05:** `check` items are **excluded from `model.content_fingerprint()`'s
  pedagogy-metadata exclusions in one direction only**: the stem and the `CASE)` set
  are content and **are** fingerprinted (editing a test case changes what the item
  asks); `[LANG:]` and `[MATCH:]` are configuration and are **not**. The planner must
  state this split explicitly in the fingerprint's docstring, which already documents
  its exclusions at `model.py:142-179`.
  — **Reversibility:** one-way — changing what is fingerprinted invalidates every
  stored `[HASH:]`.

### Execution safety and bounds

- **D-06:** **Server-side execution only.** The learner's code runs in the daemon or
  CLI process's machine, never in the browser, and never in the static offline
  `build` page. The page posts source to `/api/submit`; a bank containing `check` items
  exported to the offline page renders those items as **not answerable offline**, with
  an honest message, rather than silently scoring them wrong.
- **D-07:** Process-tree kill, per platform, with a test fixture that spawns a
  **grandchild** — Success Criterion 3 names that case specifically:
  - **POSIX:** `subprocess.Popen(..., start_new_session=True)` then `os.killpg` on
    timeout.
  - **Windows:** a Job Object created and assigned via `ctypes` with
    `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, so closing the handle kills the tree.
    `ctypes` is stdlib, so this adds no dependency. Fallback if the Job Object cannot
    be created: `taskkill /T /F /PID`. Both paths must be exercised, not just the one
    the dev machine takes.
  - The timeout is a settings key (`check.timeout_seconds`, default 5), not a constant.
- **D-08:** Two bounds beyond time, because a wall clock alone does not stop the two
  most common accidents: **output is capped** (`check.max_output_bytes`, default 64 KB,
  truncated with a stated marker, and a truncated run fails the case rather than
  hanging the reader) and **stdin is closed** after the case's input is written, so a
  program waiting on more input hits EOF instead of the timeout.
- **D-09:** `check` execution is **refused when the daemon is serving with `--lan`**,
  unless `check.allow_lan` is explicitly set true. A phone on the same wifi should not
  be able to run arbitrary code on the host by default. This is the one place where the
  honest "no sandbox" statement has a matching default, rather than only a warning.
- **D-10:** The no-sandbox statement appears in exactly two places and is worded once:
  the `SPEC` text for the `check` type, and one line of UI copy beside the editor. Both
  say the same sentence. **No documentation anywhere claims isolation, containment, or
  sandboxing** — CODE-05 is verified by grepping the repo for those words, not by
  reading intent.

### Editor

- **D-11:** A `<textarea>` plus a synchronized line-number gutter, scroll-linked, with
  Tab inserting a tab character and Shift-Tab dedenting. No CodeMirror, no Monaco, no
  external asset, no build step — the stdlib-only, no-install constraint applies to the
  browser surface too, and the vendored-asset exception is spent on KaTeX.
  The gutter is **1-based over the textarea's own lines**, so a rubric point citing
  "line 7" cites the same line the learner sees (CODE-03).
- **D-12:** The submitted answer for a `check` item is the **source text**, sent as-is.
  `public_item()` gains a `check` branch with
  `response_schema: {"type": "string", "format": "source", "language": <lang>}` and a
  starter-code field if the item authored one; `explain_payload()` reveals the per-case
  expected output only after the response. The case expectations are key material and
  do not reach the page before answering.

### Amendments after research (2026-08-08)

`05-RESEARCH.md` found a real gap in D-01 and two facts that change the task list. These
amendments are Claude's calls under the same delegated instruction and they **override** the
conflicting text above.

- **D-13 (amends D-01):** The per-case results vector is what the **scorer** compares, but it is
  **not** what the evidence records. The codebase threads exactly one `answer` value through
  `score_response()`, `evidence.response_event()`'s stored `"answer"` field, and
  `idempotency_canon` at once; storing the vector there would mean the learner's actual submitted
  code is never recorded — a regression that would show up first in Phase 8, when the tutoring
  model needs to read the specific wrong answer. Add a reserved response-event field
  (`check_source`, `null` for every other type), following the existing `error_category` /
  `hint_tier` precedent. D-01's purity argument stands unchanged; only the storage path is fixed.
  — **Reversibility:** one-way — the evidence log is append-only, so a response written without
  the source cannot gain it later.
- **D-14:** **Both** submit paths gate on the runner, not one. The browser path is
  `POST /quiz/<stem>/answer` → `handle_quiz_answer` → `quiz.record_answer()`; `/api/submit`
  (`surfaces/session.py:do_submit`) is a *separate* agent-facing path that also calls
  `score_response()` directly today. Gating only the first would let an agent driving
  `itembank submit` skip code execution entirely and score against nothing.
- **D-15:** `explain_payload(q, reveal=True)` gains a `run_result=None` parameter. There is no
  existing channel through which per-case actual output could reach it, and the UI-SPEC's
  "Your output" row requires one. This is a required signature change, not an optional one.
- **D-16 (narrows D-07):** `subprocess.Popen` **cannot** support the race-free
  `CREATE_SUSPENDED` → assign-to-job → resume sequence, because CPython's Windows
  `_execute_child` closes the child's thread handle before returning (`bpo-1677688`). Accept the
  narrow race window rather than reimplementing process creation: a grandchild spawned in the
  microseconds before job assignment can escape. That residual gap is **consistent with D-10's
  honest framing** and must be stated in the phase's own notes, not papered over. Measure the
  escape rate over 50 iterations rather than claiming zero.
- **Two regexes, not one:** `model.py`'s stem terminator (lines 43-47) **and** the separate
  `TERMINATOR` used by `assign_ids()` (lines 191-193) both need `CASE)`, `[LANG:]`, and
  `[MATCH:]` added. Fixing only the first leaves `id-assign` inserting `[ID:]`/`[HASH:]` in the
  wrong place.
- **CI is `ubuntu-latest` only.** The Windows kill path cannot be verified by CI at any point in
  this phase. It is a manual verification on the target machine, following the `01-01-PLAN.md`
  spike precedent — see `05-VALIDATION.md`'s manual table.

### Claude's Discretion

Every decision above (D-01 through D-16) is Claude's discretion under the delegated
instruction. Three specifically invite the planner to overrule:

- D-03's `::` separator, if a real Python test case's expected stdout plausibly
  contains `::`. If so, switch to the `FIELD_SEP` control-character convention
  `runtime.py:64` already established for exactly this collision, and say why.
- D-07's Job Object via `ctypes`, if it proves unreasonable to test on the target
  Windows 11 machine. The fallback path must then become the primary and the phase must
  still prove the grandchild case.
- D-09's `--lan` refusal, if it conflicts with how Phase 2's `--lan` is actually
  plumbed. The default must stay closed either way.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/ROADMAP.md` § "Phase 5: Check Item Type & Code Editor" — goal, four
  success criteria, `UI hint: yes`, and the note to **coordinate `model.py` /
  `runtime.py` diffs with Phase 1** (Phase 1 is now complete, so this reduces to
  coordinating with Phase 3, which also edits `model.py`).
- `.planning/REQUIREMENTS.md` § "Code items" — CODE-01 through CODE-05.
- `.planning/REQUIREMENTS.md` § "Subject loop" LOOP-03 and LOOP-05 — the downstream
  consumers of the runner and of D-02's config-not-code shape.
- `.planning/PROJECT.md` — stdlib-only with two named exceptions; the CSCI 1100 AI-use
  ban recorded under "Accepted risk"; one learner, no auth, no multi-tenancy (which is
  the reason D-09's `--lan` default is closed rather than permissioned).

### Prior phase context that still binds

- `.planning/phases/02.1-packaging-self-update-interop-export/02.1-CONTEXT.md` — the
  steering instruction, and the settings conventions (`x-itembank-phase`, `THIS_PHASE`
  at `surfaces/settings.py:27`, the `additionalProperties`/`required` shape) every new
  `check.*` key must follow.
- `.planning/phases/02-daemon-consolidation-settings-foundation/02-CONTEXT.md` — the
  `/api/*` route conventions and the `SystemExit`-containment rule that a runner raising
  inside the daemon must respect.

### Existing code this phase extends

- `runtime.py:1-11` module docstring — the one-scorer rule, stated as the module's own
  reason to exist. D-01 exists to keep it true.
- `runtime.py:70-101` `canonical_response()` — read the docstring at lines 71-79 before
  designing anything: it names the three consumers that must agree, one of which is the
  offline page. This is the constraint D-01 and D-06 both come from.
- `runtime.py:103-130` `canonical_key()` and `score_response()` — the two functions the
  `check` branch joins.
- `runtime.py:27-48` `public_item()` — the `response_schema` per type that D-12 extends.
- `model.py:39-120` `parse_question()` — the per-type branch structure, the `::` row
  split at lines 92-94, and the stem-terminator alternation at lines 43-47 that must
  gain `\nCASE\)` and `\n\[LANG` or the stem will swallow them.
- `model.py:280` `SPEC` and `model.py:389-401` `LINT_CODES` — the contract text and the
  sorted code tuple the new `item.check_*` codes join.
- `surfaces/quiz_page.py` — the per-type render and answer-collection JS the editor
  branch joins; also where the offline-page "not answerable offline" message from D-06
  belongs.
- `surfaces/settings.py` and `schemas/settings.schema.json` — where the `check` settings
  group (`timeout_seconds`, `max_output_bytes`, `languages`, `allow_lan`) lands, with
  `x-itembank-phase: 5`.

### Codebase maps

- `.planning/codebase/ARCHITECTURE.md` — the four layers and why `runner.py` is a peer
  of `runtime.py` rather than a surface.
- `.planning/codebase/CONCERNS.md` — read before writing the no-sandbox copy; check
  whether any existing text already overclaims.
- `.planning/codebase/TESTING.md` — `tests/*_roundtrip.py`, direct execution, no runner.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `runtime.FIELD_SEP` / `PAIR_SEP` (`runtime.py:64-67`) — the control-character
  separator convention, already justified in a comment for exactly the collision D-03
  risks.
- `model.grab()` / `model.section()` — the tag and block extraction vocabulary the
  `check` branch is built from.
- `surfaces/settings.py`'s validator with numeric bounds (added in Phase 2, plan 02-03)
  — `check.timeout_seconds` and `check.max_output_bytes` get bounds there rather than
  ad-hoc checks in the runner.
- `surfaces/day.py:339-343` — platform branching that already handles Windows vs POSIX
  cleanly; the runner's platform split should read like it, not invent a second idiom.

### Established Patterns

- **One scorer, structurally.** Not "we call the scorer" but "there is nowhere else a
  verdict can come from". D-01 is what preserves this for a type whose answer requires
  running something.
- **Pure canonical functions.** `canonical_response` and `canonical_key` take a question
  and an answer and return a string. Nothing else. Keep it that way.
- **Additive format changes only.** A bank with no `check` item parses after this phase
  exactly as before it.
- **Named dotted error codes** in a `tuple(sorted({...}))`.
- **Tests run as `python tests/<name>_roundtrip.py`** with no framework.

### Integration Points

- `model.py` — the `check` parse branch, `[LANG:]`, `[MATCH:]`, `CASE)`, `SPEC`, and the
  new `item.check_*` lint codes.
- `runner.py` (new) — execution, timeout, process-tree kill, output cap. Imports stdlib
  only; imports no surface.
- `runtime.py` — the `check` branches in `canonical_response`, `canonical_key`,
  `public_item`, and `explain_payload`.
- `surfaces/quiz_page.py` — editor field, gutter, tab handling, offline refusal message.
- `surfaces/daemon.py` — `/api/submit` calls the runner before the scorer.
- `schemas/settings.schema.json` + `schemas/item.schema.json` — new keys and the `check`
  item shape.
- `tests/check_roundtrip.py` (new) — must include the **grandchild-spawning timeout
  case** on both platforms and a multi-case pass/fail matrix.

</code_context>

<specifics>
## Specific Ideas

- The standing steering instruction: where two designs cost about the same, take the
  one that keeps a door open. Here that is D-02 (language as config, one entry shipped),
  D-04 (`MATCH` mode authored, sensible default), and D-07's settings-driven timeout.
- CSCI 1100 is the near-term consumer, and PROJECT.md records that its AI-use ban
  applies to this tool. That does not change what this phase builds — `check` runs the
  *learner's own* code and scores it deterministically, with no model involved anywhere
  in the path. Worth stating in the phase's own docs so the distinction is not lost.
- The honest-limits framing is the point of CODE-05, and it matches the project's
  posture elsewhere (`day` omits Anki counts rather than guessing; the updater fails
  silently offline rather than blocking). "This stops accidents, not escapes" is the
  same voice.

</specifics>

<deferred>
## Deferred Ideas

- **Runnable code inside lesson prose** — LOOP-03, Phase 9. It calls this runner.
- **A second language (C, JavaScript)** — a `check.languages` entry when a course needs
  it. D-02 makes it configuration; nothing here blocks it.
- **Model-marked code or model hints on a failed case** — Phase 8.
- **Real isolation** (containers, seccomp, a restricted interpreter) — out of scope
  permanently at this scale, and CODE-05 turns that into a documented property rather
  than a gap. Revisit only if a second person ever runs the tool, which is the same
  trigger as `V2-DEL-01`.
- **Per-case partial credit** — CODE-02 requires dichotomous scoring. The per-case
  vector D-01 produces makes partial credit *computable* later without a format change,
  but this phase reports pass/fail only.
- **Theming the editor** — Phase 4.

</deferred>

---

*Phase: 5-check-item-type-code-editor*
*Context gathered: 2026-08-08*
