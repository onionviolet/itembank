# Phase 9: Subject-Invariant Loop — EMT, Math, CS Integration - Research

**Researched:** 2026-08-08
**Domain:** Local-first subject-profile integration, offline mathematical rendering, and bounded lesson-code execution
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### One loop, configurable variation
- **D-01:** A versioned subject profile defines exactly the intended variation: lesson media/rendering capabilities, allowed item types, and verifier. The session loop, cursor policy, evidence, selector, and surfaces remain shared.
- **D-02:** Profiles are data selected by subject id, not Python subclasses or conditionals spread through surfaces. EMT, Math, and CS ship as three entries; adding a fourth subject is a settings/config entry plus referenced assets, not a code fork.
- **D-03:** Unknown subjects use a conservative default profile (plain markdown, existing item types, runtime scorer) and report unsupported requested capabilities explicitly.
- **D-04:** The subject id comes from namespaced objectives/bank metadata and is recorded on the session. Ambiguous mixed-subject banks require an explicit profile rather than guessing. — **Reversibility:** costly — profile selection becomes part of reproducible sessions and evidence interpretation.

### Lesson media contract
- **D-05:** Phase 3's preserved fenced-code info strings are the extension seam. Rendering produces semantic placeholders/attributes; capability adapters enhance them. The lesson parser is not forked per subject.
- **D-06:** Unsupported media renders the escaped source and an honest unavailable notice. Content never disappears and the lesson remains readable offline.

### Math
- **D-07:** Vendored KaTeX assets are bundled and served locally with no CDN/network fallback. Both inline and display math are supported through an explicit lesson syntax selected during research; raw source remains available when rendering fails.
- **D-08:** Math rendering is presentation only. Correctness still goes through existing item verifiers/runtime scoring; browser math code never scores an answer.

### Computer science
- **D-09:** Runnable lesson code calls the same bounded runner and refusal policy created for Phase 5 `check` items. No second executor, timeout, or process-tree policy is allowed.
- **D-10:** A fenced block is runnable only when its language is enabled in the subject profile and runner settings. Output, timeout, and refusal states render beside the block through the daemon; static/offline-without-daemon output remains readable but not falsely runnable.
- **D-11:** Editing/running a lesson example is ephemeral learning activity unless explicitly submitted as a `check` response; merely pressing Run does not create correctness evidence.

### EMT
- **D-12:** EMT uses the shared small markdown renderer with prose, headings, lists, and tables preserving source order and structure. No EMT-only renderer or hard-coded medical vocabulary is introduced.
- **D-13:** Tables remain accessible on narrow screens through semantic HTML and a scroll/wrap strategy chosen by UI planning; information is not flattened into screenshots.

### Integration proof
- **D-14:** One synthetic fixture per subject exercises the same lesson→item→wrong answer→hint→retry→evidence flow, varying only its profile-controlled medium/item/verifier.
- **D-15:** A fourth synthetic profile is created in tests without changing application code. This is the acceptance proof for LOOP-05, not a documentation claim.

### the agent's Discretion
Exact profile keys, math delimiters, and responsive table presentation remain for research/UI planning. The shared-loop and no-second-runner/scorer/parser invariants are locked.

### Deferred Ideas (OUT OF SCOPE)
- Objective scheduling and cross-subject daily pacing — Phase 10.
- Subject-specific content authoring — private-bank work, not repository implementation.
- Additional language runners — profile extension when a real course needs one.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LOOP-01 | One subject-invariant loop drives EMT, Math, and CS; only lesson medium, allowed item types, and verifier vary | Data-driven, versioned profile selection; session-owned selected profile; one shared feedback/runtime/evidence path. |
| LOOP-02 | Math lessons and items render LaTeX offline from a vendored asset, with no CDN and no build step | Vendored KaTeX distribution, local resource serving, ordered inline/display delimiters, and an unplugged-browser regression test. |
| LOOP-03 | CS lessons carry runnable code inside the prose | Semantic fenced-code adapter and daemon endpoint that invokes the Phase 5 runner once, without evidence writes for Run. |
| LOOP-04 | EMT lessons render prose and tables | Existing small renderer remains the only renderer; semantic table markup and narrow-screen overflow are covered by fixture/UI tests. |
| LOOP-05 | Adding a fourth subject requires configuration, not a fourth surface | Test-only fourth profile loads through the public profile loader and completes the common fixture flow with no application-code edit. |
</phase_requirements>

## Summary

Phase 9 is an integration boundary, not three subject features. The planner should introduce one versioned profile registry and one deterministic profile-selection function before touching presentation. The profile supplies capabilities and allowed types; the existing lesson reader, feedback state machine, scorer, runner, evidence writer, daemon, and CLI remain the owners of their existing responsibilities. This is the only design that makes LOOP-05 mechanically provable. [VERIFIED: `09-CONTEXT.md`, D-01 through D-15]

Math should be a local KaTeX presentation adapter over the reader's escaped text nodes, using `$$...$$` for display and `$...$` for inline expressions. KaTeX documents that delimiter ordering matters: the `$$` rule must precede `$`; its auto-renderer also skips `pre` and `code`, preserving source code fences. Its browser distribution requires the fonts directory to stay beside the stylesheet, so the release allowlist must explicitly carry the complete vendored distribution rather than individual JavaScript files. [CITED: https://katex.org/docs/autorender.html] [CITED: https://katex.org/docs/browser.html]

Runnable lesson examples are a distinct interaction from assessable `check` items. The daemon may invoke the Phase 5 bounded runner after server-side profile/settings validation, but it must return observation only and write no correctness event. The existing source already derives evidence subjects from namespaced objectives, but current sessions record only an objective; Phase 9 must add a selected profile/subject field through the session-upgrade path to make a resumed session reproducible. [VERIFIED: `evidence.py:306-314` — `return objective.split(":", 1)[0]`] [VERIFIED: `surfaces/session.py:76-80` — `"objective": objective or "", "seed": seed,`]

**Primary recommendation:** Establish `subject_profiles` as a schema-validated, versioned settings object; make the runtime select and persist exactly one profile, then attach math and code behavior solely as renderer/daemon adapters to the Phase 3 and Phase 5 seams. [ASSUMED]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Profile validation and selection | API / Backend | Database / Storage | Selection is session-reproducibility policy and must not be inferred by a browser. |
| Profile persistence | Database / Storage | API / Backend | Session JSON records the resolved subject/profile so a resumed sitting cannot reinterpret a bank. |
| Lesson markdown and EMT tables | Frontend Server (SSR) | Browser / Client | The reader produces safe semantic HTML; CSS provides only responsive presentation. |
| Offline LaTeX | Browser / Client | CDN / Static | Local static KaTeX assets transform lesson text after render; no request reaches a CDN. |
| Runnable lesson code | API / Backend | Browser / Client | The browser requests an execution; the daemon enforces profile/language/network policy and invokes the one runner. |
| Correctness and hints | API / Backend | Database / Storage | The existing runtime feedback policy and scorer own verdicts; evidence records the resulting learning path. |

## Standard Stack

### Core

| Library / component | Version | Purpose | Why standard |
|---------------------|---------|---------|--------------|
| Python standard library | 3.11+ in CI; 3.13.5 available locally | Profile loader, daemon, session upgrades, HTML, tests | Project constraint forbids a new runtime dependency. [VERIFIED: `.github/workflows/ci.yml:10-12` — `python-version: "3.11"`] |
| Existing `model` / `runtime` / `evidence` layers | repository source | Parse, score, transition, and record one loop | `score_response` remains the sole verdict function: `return canonical_response(q, answer) == key`. [VERIFIED: `runtime.py:350-360`] |
| Vendored KaTeX distribution | Pin an audited release; current registry latest is 0.18.2 (published 2026-08-08) | Client-side LaTeX presentation with local JavaScript, CSS, and fonts | Its official auto-render API supports ordered delimiters and non-throwing render behavior. [CITED: https://katex.org/docs/autorender.html] [CITED: https://katex.org/docs/options] |

### Supporting

| Library / component | Version | Purpose | When to use |
|---------------------|---------|---------|-------------|
| Phase 3 `surfaces/lesson.py` contract | upstream Phase 3 artifact | Semantic fenced-code language classes and escaped reader markup | Enhance its emitted HTML; never reparse lesson markdown in Phase 9. [VERIFIED: `03-CONTEXT.md`, D-05] |
| Phase 5 `runner.py` contract | upstream Phase 5 artifact | Time-bounded, output-capped execution with process-tree cleanup | Only for a profile-enabled language and an enabled runner setting; never for math or EMT. [VERIFIED: `05-CONTEXT.md`, D-01 through D-02] |
| `resources.read_bytes()` | repository source | Read bundled bytes from a checkout or `.pyz` | Use for local KaTeX asset serving/loading when the artifact is zipped. [VERIFIED: `resources.py:33-45`] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Data profile registry | Subject subclasses / per-subject surfaces | Contradicts D-02 and makes fourth-subject proof impossible. |
| Vendored KaTeX | CDN script tag | Contradicts unplugged offline requirement. |
| Phase 5 runner call | New lesson-code executor | Duplicates process, timeout, cap, and refusal policy in direct conflict with D-09. |
| Semantic HTML table | Screenshot/image table | Loses structure and accessibility, contradicting D-13. |

**Installation:** None. Do not add `npm install`, a browser build step, or a Python package. Vendor a reviewed KaTeX release as files only. [VERIFIED: `PROJECT.md`, Constraints]

**Version verification:** `npm view katex version time --json` reported `0.18.2`, published 2026-08-08. The asset is not an application dependency, but a same-day vendor update requires human review before it is copied into the repository. [VERIFIED: npm registry]

## Package Legitimacy Audit

No package is installed in this phase. This audit exists because a third-party browser asset is vendored.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `katex` [WARNING: flagged as suspicious — verify before using.] | npm | latest published 2026-08-08 | 21,120,031/week | github.com/KaTeX/KaTeX | SUS (recency only) | Do not install; add `checkpoint:human-verify` before vendoring the chosen release files. |

**Packages removed due to [SLOP] verdict:** none.

**Packages flagged as suspicious [SUS]:** `katex`; the legitimacy seam reports a trusted upstream repository and high download count, but flags the latest release as too new. [VERIFIED: npm registry]

## Architecture Patterns

### System Architecture Diagram

```text
bank metadata / namespaced objective + explicit override
                         |
                         v
              profile loader + validation
                    | known | unknown/mixed
                    |       +--> conservative profile + explicit capability notice
                    v
      persisted session {subject, profile version/id}
                         |
                         v
lesson parser -> semantic HTML -> profile capability adapters
      |                         |                     |
      |                         |                     +--> code fence -> daemon -> Phase 5 runner
      |                         |                                      |           |
      |                         |                                      +-- refusal / output / timeout
      |                         +--> math text -> local KaTeX JS/CSS/fonts
      |                                                    |
      +--> EMT prose/list/table --------------------------+
                         |
                         v
lesson -> item -> wrong answer -> Phase 6 hint -> retry
                         |
                         v
             runtime.score_response -> append-only evidence
```

### Recommended Project Structure

```text
subjects.py                  # profile schema-neutral loader, selector, capability checks [ASSUMED]
schemas/settings.schema.json # published profile settings contract
surfaces/lesson.py           # semantic adapter hooks and unavailable fallbacks
surfaces/daemon.py           # one guarded lesson-run route and local asset route
vendor/katex/                # reviewed KaTeX CSS, JS, auto-render JS, and fonts [ASSUMED]
tests/subject_loop_roundtrip.py
tests/math_offline_roundtrip.py
```

### Pattern 1: Versioned data profile, selected once

**What:** Validate profile entries at settings load, resolve the profile from an explicit override or an unambiguous subject identifier, and persist the resolved id plus profile version in session JSON. Treat profile capabilities as allowlists, not browser hints. [ASSUMED]

**When to use:** Every `start` path, including the daemon API. `next`, `submit`, `hint`, and resume read the persisted selection rather than resolving the bank again. This preserves the evidence/interpretation boundary locked by D-04. [VERIFIED: `09-CONTEXT.md`, D-04]

**Implementation guidance:** Start with a dedicated pure selector module; it must import no surface. Its output should feed the existing session and feedback policy rather than creating subject-specific runtime branches. Validate an ambiguous bank before session creation; do not infer from the first item. [ASSUMED]

### Pattern 2: Enhance semantic reader output, never parse twice

**What:** Phase 3 preserves code-fence info strings as a sanitized language class and escapes code content. Phase 9 should add stable attributes/placeholders at this output seam, then run only enabled adapters against those nodes. [VERIFIED: `03-CONTEXT.md`, D-05]

**When to use:** Math adapter targets only lesson content text, explicitly skipping code fences. Code adapter targets only profile-enabled `language-*` fences. Unsupported/missing adapters show escaped source and an unavailable notice. [VERIFIED: `09-CONTEXT.md`, D-06 through D-07]

### Pattern 3: One runner, observation-only lesson execution

**What:** A lesson Run request validates the stored profile, fence language, current runner settings, and LAN refusal policy before calling Phase 5's bounded runner. It returns output/status beside the block but does not pass any vector to `score_response` or `evidence.response_event`. [VERIFIED: `09-CONTEXT.md`, D-09 through D-11]

**When to use:** Only while the daemon is present. The static `lesson` output retains readable source and omits/marks unavailable controls, because it cannot honestly execute code. [VERIFIED: `09-CONTEXT.md`, D-10]

### Pattern 4: Profile matrix fixture, not three test stacks

**What:** Build one shared test driver whose subject cases differ only in profile and synthetic source medium. Assert identical runtime transitions and evidence shape, then add a fourth profile solely through config in the test. [VERIFIED: `09-CONTEXT.md`, D-14 through D-15]

## Code Examples

### KaTeX adapter example

```javascript
renderMathInElement(lesson, {
  delimiters: mathDelimiters,
  throwOnError: false,
  trust: false
});
```

Use ordered `mathDelimiters` with display `$$...$$` before inline `$...$`; include `\\(...\\)` and `\\[...\\]` only if the published lesson grammar intentionally supports them. `throwOnError: false` preserves readable source for invalid LaTeX, while `trust: false` keeps raw-HTML/resource-affecting commands disabled. [CITED: https://katex.org/docs/autorender.html] [CITED: https://katex.org/docs/options]

### Anti-Patterns to Avoid

- **Profile checks spread through templates:** one new `if subject == ...` in a surface becomes a fourth-subject code change. Centralize selection and capability checks. [VERIFIED: `09-CONTEXT.md`, D-02]
- **Auto-rendering all of `document.body`:** it risks transforming chrome or dynamically rendered result text. Target the lesson-content element only. [ASSUMED]
- **Copying only KaTeX JavaScript:** CSS references relative font URLs; copy the matching font tree and test offline. [CITED: https://katex.org/docs/browser.html]
- **Writing lesson Run events as responses:** this would fabricate correctness evidence for an exploratory activity. [VERIFIED: `09-CONTEXT.md`, D-11]
- **Client-side language/profile authorization:** the daemon must revalidate because browser attributes are editable. [ASSUMED]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Mathematical layout | Custom TeX parser or regex replacement | Vendored KaTeX auto-render adapter | TeX grammar, browser typography, MathML accessibility, and errors are already addressed by the renderer. [CITED: https://katex.org/docs/autorender.html] |
| Code execution | Lesson-specific subprocess logic | Phase 5 bounded `runner.py` path | Timeout, output cap, process-tree cleanup, language allowlist, and LAN refusal are security-sensitive and already one contract. [VERIFIED: `05-CONTEXT.md`, D-01 through D-02] |
| Markdown/EMT renderer | A second medical markdown renderer | Phase 3 small shared renderer | Its fenced-code and table structure is the explicit downstream seam. [VERIFIED: `03-CONTEXT.md`, D-08] |
| Subject extensibility | Class hierarchy or a fourth route | Schema-validated profile data | LOOP-05 requires a configuration-only extension proof. [VERIFIED: `09-CONTEXT.md`, D-15] |

**Key insight:** Every variable feature is declarative capability data; every correctness, state transition, and dangerous action remains owned by the already shared runtime boundary. [VERIFIED: `09-CONTEXT.md`, D-01]

## Common Pitfalls

### Pitfall 1: Shipping incomplete vendored assets

**What goes wrong:** Math works during a CDN-backed development check but fonts or scripts fail from a `.pyz` or unplugged browser.

**Why it happens:** KaTeX CSS uses relative font URLs, and the current build stages only the `surfaces` and `schemas` directories: `STAGE_DIRS = ("surfaces", "schemas")`. [VERIFIED: `build.py:28-35`]

**How to avoid:** Vendor a complete reviewed distribution; extend the explicit build allowlist; access bundled bytes through `resources.read_bytes`; and run an offline rendered-page test after packaging. [VERIFIED: `resources.py:33-45`]

**Warning signs:** Browser network panel requests an external host, or a packaged page renders text with missing-glyph boxes. [ASSUMED]

### Pitfall 2: Delimiter collision and code-fence corruption

**What goes wrong:** `$$...$$` becomes an empty inline expression, or TeX-like source inside a code block is unexpectedly transformed.

**Why it happens:** Auto-render matches delimiters in order and normally ignores `pre`/`code` nodes. [CITED: https://katex.org/docs/autorender.html]

**How to avoid:** Make `$$` first, document `$...$` and `$$...$$` in the lesson contract, run the adapter only on reader content, and preserve the Phase 3 escaped code nodes.

**Warning signs:** Display equations render blank or runnable Python strings containing `$` change in the reader. [ASSUMED]

### Pitfall 3: Session profile drift after resume

**What goes wrong:** A bank/config edit changes the subject behavior midway through a sitting.

**Why it happens:** Current session state retains a selected item list, mode, objective, and seed but no selected subject/profile. [VERIFIED: `surfaces/session.py:76-80` — `"responses": [], "status": "active", "mode": mode,` and `"objective": objective or "", "seed": seed,`]

**How to avoid:** Version the session addition, add an upgrade, persist resolved profile id/version at start, and make resume consume that stored value.

**Warning signs:** A resume result changes allowed types, adapters, or verifier after a settings edit. [ASSUMED]

### Pitfall 4: Treating Run as assessment

**What goes wrong:** An execution button advances a cursor, unlocks a hint, or adds an evidence response.

**Why it happens:** Both features happen to call the runner, but they have different pedagogical meanings.

**How to avoid:** Keep lesson Run on a separate daemon action that returns only process observation; only normal `check` submission reaches runtime scoring/evidence. [VERIFIED: `09-CONTEXT.md`, D-09 through D-11]

**Warning signs:** A Run-only interaction appears in an evidence query or report. [ASSUMED]

### Pitfall 5: KaTeX trust escalation on bank-authored content

**What goes wrong:** A bank can request HTML attributes or external resources through math commands.

**Why it happens:** KaTeX documents that `trust` enables commands such as `\includegraphics` and `\htmlClass`; the default is false. [CITED: https://katex.org/docs/security] [CITED: https://katex.org/docs/options]

**How to avoid:** Explicitly retain `trust: false`, set bounded expansion/size options during implementation, and test hostile TeX content as literal/error output. [CITED: https://katex.org/docs/security]

**Warning signs:** A math fixture creates arbitrary classes, links, images, or network requests. [ASSUMED]

## State of the Art

| Old approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| Fence as inert preformatted source | Phase 3 semantic language class | Phase 3 plan contract | Phase 9 can add behavior without a second parser. [VERIFIED: `03-CONTEXT.md`, D-08] |
| CDN math snippets | Complete local KaTeX distribution | This phase | Supports network-unplugged math and reproducible packaging. [CITED: https://katex.org/docs/browser.html] |
| Per-subject app logic | Data-selected profile + shared loop | This phase | Fourth subject becomes a configuration test case. [VERIFIED: `09-CONTEXT.md`, D-02 and D-15] |

**Deprecated/outdated:** Do not use the KaTeX CDN snippets shown in documentation. They demonstrate loading order, but conflict with D-07's no-network requirement. [CITED: https://katex.org/docs/autorender.html]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The profile registry should be a `subject_profiles` object in `itembank.json` rather than a new standalone file. | Summary / Pattern 1 | Planner may need to choose a different schema location while preserving D-01 through D-04. |
| A2 | The selector module should be named `subjects.py`. | Recommended Project Structure | Naming only; no architectural impact. |
| A3 | The exact KaTeX release should be chosen by a human after reviewing the same-day latest release rather than automatically pinning it. | Package Legitimacy Audit | A release-specific issue could remain if review is skipped. |
| A4 | The reader adapter should target a dedicated lesson-content element rather than `document.body`. | Anti-Patterns | A broader target could alter chrome or future dynamic content. |
| A5 | Narrow-table behavior will be horizontal scroll within an accessible semantic table. | Architectural / UI | UI planning may select wrapping with equivalent accessibility instead. |

## Open Questions

1. **Where will the versioned profile registry live?**
   - What we know: Settings schema is the published configuration boundary and currently rejects unknown top-level keys: `"additionalProperties": false`. [VERIFIED: `schemas/settings.schema.json:7-10`]
   - What's unclear: Whether profiles need independent bank-local distribution or only user settings.
   - Recommendation: Put the initial registry in settings because LOOP-05 explicitly calls for configuration; preserve an internal loader boundary so a future bank-local source can remain additive. [ASSUMED]

2. **Which KaTeX release should be vendored?**
   - What we know: Registry latest `0.18.2` was published today and package legitimacy returns SUS for recency. [VERIFIED: npm registry]
   - What's unclear: The reviewed release/version and license-notice workflow the repository will accept.
   - Recommendation: Add a human checkpoint that verifies the upstream release contents, license, checksum/source tag, and chosen immutable version before it enters `vendor/`. [ASSUMED]

3. **How should narrow EMT tables behave?**
   - What we know: D-13 locks semantic tables and forbids screenshot flattening.
   - What's unclear: Whether the UI contract prefers horizontal scroll, controlled wrapping, or a hybrid.
   - Recommendation: Resolve in Phase 9 UI planning; acceptance must retain `table`, header, and cell semantics at the narrow viewport. [ASSUMED]

4. **Are Phases 3, 5, and 6 implemented before Phase 9 execution begins?**
   - What we know: Phase 9 depends on all three, while the current checkout has none of `surfaces/lesson.py` or `runner.py`. [VERIFIED: repository source inventory, 2026-08-08]
   - What's unclear: Execution order versus planning order.
   - Recommendation: First plan task must assert upstream public contracts/tests exist; block implementation rather than recreating their behavior. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | Runtime/tests | ✓ | 3.13.5 local; CI is 3.11 | Project minimum CI target remains 3.11. |
| Node/npm | One-time KaTeX release inspection only | ✓ | Node v22.22.3 / npm 11.5.1 | Direct reviewed release archive; never an application install. |
| Vendored KaTeX files | LOOP-02 | ✗ (not yet in repository) | — | Explicit unavailable/raw-source math state until the reviewed asset is added. |
| Phase 3 reader | LOOP-01 through LOOP-04 | ✗ (planned upstream) | — | No fallback; do not reimplement it in Phase 9. |
| Phase 5 runner | LOOP-03 | ✗ (planned upstream) | — | Static readable code fence only; daemon Run capability remains unavailable. |
| Phase 6 feedback policy | LOOP-01 integration proof | ✗ (planned upstream) | — | No fallback; fixture may not claim hint-loop behavior without it. |

**Missing dependencies with no fallback:** the upstream Phase 3/5/6 contracts for full LOOP-01 through LOOP-04 verification.

**Missing dependencies with fallback:** vendored KaTeX and runner capability have explicit readable/unavailable states, but those states do not satisfy the final requirements and must not be accepted as completion.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Direct Python roundtrip scripts; no external test framework. [VERIFIED: `.github/workflows/ci.yml:66-74`] |
| Config file | None — CI iterates `tests/*.py`. [VERIFIED: `.github/workflows/ci.yml:66-74`] |
| Quick run command | `python tests/subject_loop_roundtrip.py` |
| Full suite command | `Get-ChildItem tests\*.py | ForEach-Object { python $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| LOOP-01 | EMT, Math, and CS execute identical lesson→wrong→hint→retry→evidence transitions under different profiles | integration | `python tests/subject_loop_roundtrip.py` | ❌ Wave 0 |
| LOOP-02 | Vendored CSS/JS/fonts render inline/display expressions with networking disabled | browser/integration | `python tests/math_offline_roundtrip.py` | ❌ Wave 0 |
| LOOP-03 | Profile-enabled lesson code runs through the existing bounded runner; static/LAN/refusal states are honest and Run records no evidence | integration | `python tests/lesson_code_roundtrip.py` | ❌ Wave 0 |
| LOOP-04 | EMT source prose, lists, and tables retain semantic order/markup and narrow layout behavior | unit/integration | `python tests/lesson_roundtrip.py` | ❌ upstream Wave 0 |
| LOOP-05 | Fourth synthetic profile works from configuration only and no subject-specific application branch is added | integration/source guard | `python tests/subject_loop_roundtrip.py` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** affected roundtrip script plus `python tests/scoring_roundtrip.py`.
- **Per wave merge:** all relevant lesson/check/hint/subject tests.
- **Phase gate:** full test suite green and a manual network-unplugged math check against the packaged artifact.

### Wave 0 Gaps

- [ ] `tests/subject_loop_roundtrip.py` — profile matrix, shared loop, fourth-subject proof.
- [ ] `tests/math_offline_roundtrip.py` — no CDN request, complete local font asset set, inline/display/error fallback.
- [ ] `tests/lesson_code_roundtrip.py` — single runner invocation contract, no evidence for Run, policy refusals.
- [ ] Upstream `tests/lesson_roundtrip.py`, `tests/check_roundtrip.py`, and `tests/hint_roundtrip.py` — prerequisite contracts from Phases 3, 5, and 6.
- [ ] Packaged-artifact test that asserts explicit asset allowlisting after the KaTeX directory is added.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V1 Architecture, Design and Threat Modeling | yes | Separate profile selection, presentation, execution, scoring, and evidence ownership; document the non-sandbox runner boundary. [CITED: https://devguide.owasp.org/en/06-verification/01-guides/03-asvs/] |
| V2 Authentication | no | Single-user local application; no accounts or identity boundary in phase scope. [VERIFIED: `PROJECT.md`, Constraints] |
| V3 Session Management | yes | Versioned session upgrade; persist selected profile and never infer it again on resume. |
| V4 Access Control | yes | Server-side capability/profile/language/LAN checks before invoking the runner. |
| V5 Validation, Sanitization and Encoding | yes | Schema-validate profiles, allowlist languages/capabilities, retain HTML escaping, and reject unsafe route identifiers. OWASP identifies positive validation and context-specific output encoding as applicable controls. [CITED: https://cornucopia.owasp.org/taxonomy/asvs-4.0.3/05-validation-sanitization-and-encoding/01-input-validation] [CITED: https://cornucopia.owasp.org/taxonomy/asvs-4.0.3/05-validation-sanitization-and-encoding/03-output-encoding-and-injection-prevention] |
| V6 Stored Cryptography | no | No new credential, secret, or encrypted storage design in this phase. |
| V12 Files and Resources | yes | Explicit static-asset allowlist; no bank-controlled filesystem path is converted into an asset path. |
| V13 API and Web Service | yes | One bounded daemon Run endpoint with JSON validation and no path/evidence leakage. |
| V14 Configuration | yes | Profiles become published, typed settings rather than unvalidated template flags. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Bank-authored HTML/TeX reaches lesson DOM | Tampering | Escape lesson source before rendering; retain KaTeX `trust: false`; test hostile `\html*`/resource commands as unavailable/error text. [CITED: https://katex.org/docs/security] |
| Browser calls Run with disabled language/profile | Elevation of privilege | Recompute capability and settings policy server-side before the Phase 5 runner call. [ASSUMED] |
| LAN-exposed daemon runs code | Elevation of privilege | Reuse Phase 5 LAN refusal/allowlist contract; do not duplicate or relax it for lessons. [VERIFIED: `09-CONTEXT.md`, D-09 through D-10] |
| Asset path traversal or unbundled resource access | Information disclosure | Map only known KaTeX asset filenames through the resource reader and build allowlist; never concatenate a browser path to disk. [ASSUMED] |
| Math macro expansion / oversized rendering | Denial of service | Configure bounded KaTeX `maxExpand` and `maxSize`, and retain parse-error fallback. [CITED: https://katex.org/docs/security] |
| Exploratory Run pollutes learning record | Repudiation / integrity | Keep Run outside submit/scorer/evidence flow; prove zero added response events. [VERIFIED: `09-CONTEXT.md`, D-11] |

## Sources

### Primary (HIGH confidence)

- [Project Phase 9 context](.planning/phases/09-subject-invariant-loop-emt-math-cs-integration/09-CONTEXT.md) - locked integration decisions and scope.
- [Current runtime source](runtime.py) - single scoring boundary and versioned session pattern.
- [Current evidence source](evidence.py) - namespaced objective subject extraction and append-only response event shape.
- [Current build source](build.py) - explicit bundled-resource allowlist.

### Secondary (MEDIUM confidence)

- [KaTeX auto-render documentation](https://katex.org/docs/autorender.html) - ordered delimiters, ignored tags, auto-render API.
- [KaTeX browser documentation](https://katex.org/docs/browser.html) - local distribution and CSS-relative font requirement.
- [KaTeX options and security documentation](https://katex.org/docs/options) - error and trust behavior; [security page](https://katex.org/docs/security) - untrusted-input controls.
- [OWASP ASVS overview](https://devguide.owasp.org/en/06-verification/01-guides/03-asvs/) - applicable category map.

### Tertiary (LOW confidence)

- None. Design choices needing confirmation are listed in the Assumptions Log.

## Metadata

**Confidence breakdown:**

- Standard stack: MEDIUM - KaTeX behavior is documented officially, but the chosen vendored release requires a same-day-release human check.
- Architecture: HIGH - the shared-loop, parser, scorer, runner, and profile invariants are locked Phase 9 decisions and grounded in current code/upstream contracts.
- Pitfalls: MEDIUM - KaTeX asset/security concerns are officially documented; exact profile module/schema design remains an explicit assumption.

**Research date:** 2026-08-08
**Valid until:** 2026-08-15 for KaTeX release selection; 2026-09-07 for project-internal architecture.
