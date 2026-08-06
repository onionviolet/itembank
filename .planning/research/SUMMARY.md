# Project Research Summary

**Project:** itembank — local-first, AI-taught learning platform (single learner: EMT, Math 1400, CSCI 1100)
**Domain:** Local-first assessment-and-teaching runtime, extending a stdlib-only Python 3 protocol/runtime into a comprehensive learning platform
**Researched:** 2026-08-05
**Confidence:** MEDIUM-HIGH overall

## Executive Summary

itembank is not a green-field build — it is six-plus narrow capability additions to a working stdlib-only Python runtime, and every research thread agrees: extend, don't replace. Math rendering gets vendored KaTeX (~700KB, zero network), learner code execution gets `subprocess` + `timeout` + POSIX `resource` (with an explicit, honest "not a sandbox" posture), the code editor is a plain `<textarea>` with a hand-written gutter, packaging is `python -m zipapp`, and the self-updater is `urllib` + `hashlib` against GitHub Releases. All four researchers converge on one architectural centerpiece: an event-sourced evidence store (single append-only log, everything else a projection) sitting behind a formalized Operations API in `runtime.py` that both the CLI and a new consolidated daemon call identically.

The single biggest reframe this synthesis must carry: PROJECT.md was revised after research ran, and the tutoring model now sees the key and rationale — FEATURES.md's "key-blind model" framing is stale. The real, still-substantial advantage is that the runtime, not a system prompt, decides which hint tier the model may speak at, and drops model output that reaches past that tier — a structural, code-enforced disclosure gate rather than a persuadable instruction, genuinely different from every AI-tutor product researched, but requiring a new enforcement mechanism no prior research file designed. Hosted models are now explicitly permitted (an accepted risk), which removes "offline-only" as a model-layer constraint but does not relax the requirement that the core loop degrade gracefully, never block, when the network is down.

The primary risk is scope-shaped, not technology-shaped: 45+ requirements in one milestone, on a codebase whose compatibility floor never goes away, has the structural signature of a big-bang build. The antidote all threads agree on: stable IDs + one evidence store must land first and be a fully-closed, demoable checkpoint before anything downstream consumes it, and every later phase must close in a genuinely shippable state. A second, sharper risk sits inside the auditor: giving an LLM write access to the bank and the job of judging curriculum coverage reintroduces the project's own founding failure one layer up — `lint`-clean is not quality-clean, and reversibility is a recovery property, not a detection property.

## Key Findings

### Recommended Stack

Stack additions are stdlib-scoped with exactly two named non-stdlib exceptions (vendored KaTeX, `urllib`), both already accepted. Nothing here asks for a third. HIGH confidence throughout except two flagged MEDIUM items: the Chromium `--app=` switch (community-documented, not official) and GitHub's release-asset `digest` field exact format (existence confirmed, literal shape unverified).

**Core technologies:**
- KaTeX 0.18.1 (vendored, ~700KB) — LaTeX rendering, offline, no CDN
- `subprocess.run(timeout=N)` + POSIX `resource.setrlimit` + `taskkill /T /F` on Windows — runs `check`-item code; stops accidents, not deliberate escapes
- Plain `<textarea>` + hand-written gutter — code editor; CodeMirror/Monaco/Ace rejected as disproportionate
- `python -m zipapp` — double-clickable `.pyz`/`.pyzw` packaging; PyInstaller/Nuitka rejected (compiled, prior Defender false-positive)
- `urllib.request` + `hashlib.sha256` + `os.replace()` — self-updater; checksum is integrity-only, not authenticity
- `ModelAdapter` ABC over `subprocess` (Claude Code/Codex) and `urllib` POST to `/v1/chat/completions` (Ollama/llama.cpp) — one interface, hosted or local is a config change

**Post-PROJECT.md-revision framing correction:** anything in STACK.md framed as "hosted forbidden" should read "hosted permitted, accepted risk" — the adapter's OpenAI-compatible design already treats hosted/local as one code path, so no stack change is needed, only a framing correction.

### Expected Features

**Must have (table stakes), already partly shipped and extended this milestone:** instant feedback with attached explanation (`study` currently drops `opts`/`da`/`second`/`notes`); multiple item types including a verifier-backed `check`; spaced review at the objective level (card-level stays with Anki — a genuine either/or); a pacing gate against single-sitting bingeing; resumable persisted progress (shipped); plain-text versionable authoring; hints that don't hand over the answer; visible history over time (currently split across three stores).

**Should have (differentiators), reframed per PROJECT.md's revision:**
- **Runtime-enforced hint-tier disclosure control** (revised from "key withholding") — model sees the key/rationale, runtime gates the tier and drops output past it. Still the single biggest structural advantage over every AI-tutor examined, but now needs an explicit enforcement check that a key-blind design didn't require.
- Deterministic hint ladder over authored `da` distractor analysis (~100% authored coverage in the live EMT bank)
- One evidence store feeding selection, pacing, and a syllabus-coverage auditor — no examined competitor does the coverage-audit piece
- One subject-invariant loop across prose/LaTeX/code
- Git-evidence trail as the progress signal, not points/badges
- Machine-readable format contract + linter an authoring agent self-corrects against
- GIFT export as cheap one-way interop

**Defer (v1.x/v2+):** selection modes, decay flagging, weak-objective weighting (need real evidence history); auditor draft-and-approve/full autonomy (only after report-only is trusted); full SRS ownership merged with Anki (conflicts with the "Anki owns cards" decision — a genuine either/or); randomized item variants (solves a classroom-cheating problem this single-learner tool doesn't have); bounded NL restatement of unlocked hints; compiled binary packaging; local model backend (hardware-gated).

**Anti-features reaffirmed:** gamification, chat-box-as-primary-tutor, hosted accounts/social layer, data-hungry per-user BKT/FSRS personalization (needs population-scale data one learner won't produce), content marketplace, native mobile app, video lecture hosting, team/competitive multiplayer, push notifications, auto-grading prose without a review state.

### Architecture Approach

Extends the existing four-layer split (`model`/`runtime`/`server`/`surfaces`), adding `evidence`/`scheduler` layers and `adapters/`/`auditor/` packages without re-architecting what works. The load-bearing decision: formalize `runtime.py` as an Operations API — every state-changing capability is one plain function the CLI and daemon both call identically, making "every capability reachable from both surfaces" structural rather than convention.

**Major components:**
1. `evidence.py` — append-only NDJSON event log; everything else (session state, attempt view, day log, longitudinal history) is a replay-computed projection; corrections are compensating events
2. `runtime.py` (Operations API) — the only module deciding correctness or hint-tier reveal; the seam both CLI and daemon call
3. `scheduler.py` — objective due-today, daily cap, decay flagging; pure consumer, writes nothing but an optional audit event
4. `auditor/` — syllabus ingest → coverage map → draft (via adapter) → `model.lint()` gate → reversible write, autonomy read from config
5. `adapters/` — vendor-neutral `ModelAdapter` ABC; client of runtime ops as tutor, supplier of draft text as author; never scores directly
6. `surfaces/daemon.py` + `surfaces/api.py` — one consolidated loopback process (strangler-fig migration off per-subcommand servers)

**Key patterns:** event-sourced evidence; content-hash ID minted once at first lint then pinned as opaque/immutable (open decision below); idempotent `submit` via the natural key `(session_id, item_id, attempt_no)`; strangler-fig daemon consolidation.

### Critical Pitfalls

1. **Content-hash IDs silently orphan evidence history on every edit** — the single open design decision every researcher flagged; must be resolved explicitly (see below).
2. **The auditor confidently declares curriculum coverage that doesn't exist** — LLM calibration research shows highest-confidence outputs are disproportionately wrong on low-resource local documents (exactly this project's syllabi). Require a citation per coverage claim as a structural contract, not a prompt instruction.
3. **Full auditor autonomy causes rubber-stamped drift, not caught mistakes** — `lint`-clean does not equal truth; reversibility is recovery, not detection. One-item-per-commit, distinct authorship tagging, a second quality gate before full autonomy.
4. **LLM-generated items pass `lint` while failing as items** — implausible distractors, answer-leaking stems, near-duplicates, invisible to a format linter. Needs a distinct distractor-quality/duplicate pass reused by the auditor.
5. **Overstating what `check`-item execution protects against** — a timeout stops accidents, not deliberate escapes; must never be upgraded to a claim of sandboxing in code, docs, or UI copy. Code must only ever come from the person at the keyboard.
6. **45+ requirements in one milestone reintroduces a big-bang shape** — mitigated only by making every phase boundary a genuinely demoable checkpoint.

## Implications for Roadmap

All four researchers' build-order proposals converge tightly and are reconciled here into one ordering. ARCHITECTURE.md's 12-step sequence is the most granular and is adopted as the backbone; FEATURES.md's dependency graph and PITFALLS.md's phase-mapping both independently confirm the same load-bearing fact — stable IDs and the evidence store must land, fully migrated, before anything reads/writes against them — so no reconciliation conflict exists there. The one place sources differ is granularity: FEATURES.md groups by "MVP loop" while ARCHITECTURE.md interleaves daemon plumbing and settings scaffolding earlier as explicit parallel tracks. This synthesis follows ARCHITECTURE.md's finer-grained ordering because it names genuine parallel-work opportunities explicitly, which matters for a 45-requirement milestone where the pitfall is false single-critical-path shape.

### Phase 1: Evidence Spine — Stable IDs, Event Log, Migration
**Rationale:** Every researcher independently identifies this as the hard dependency root.
**Delivers:** `model.py` ID minting + `FORMAT-VERSION` + machine-readable lint codes; `evidence.py` append/replay/idempotency; migration/backfill of `_attempts/*.md`, session JSON, `daily_log.md` into tagged events. Existing surfaces must be fully re-pointed and working against the new store before this phase closes — migration-and-parity is its own checkpoint, not folded into "evidence spine done."
**Avoids:** Pitfall 1 and Pitfall 7 — this phase is the demoable checkpoint proving the milestone isn't one undividable block.
**Open decision to resolve here, not defer:** opaque ID + content-hash-as-fingerprint-field (evidence keyed to the opaque ID) versus content-hash-as-the-literal-ID with a mandatory rekey/alias table written automatically on every `lint`-detected near-collision. The roadmap must pick one and make "edit an item, confirm evidence history still resolves" an acceptance test either way.

### Phase 2: Daemon Plumbing (parallel-eligible with Phase 1)
**Rationale:** Pure HTTP scaffolding has zero dependency on the evidence spine.
**Delivers:** `surfaces/daemon.py` route table, `Handler` subclass, KaTeX static-file route.
**Implements:** Strangler-fig daemon consolidation — old servers stay runnable, retired route by route later.

### Phase 3: LESSON Format + Settings Scaffold (parallel-eligible with Phase 1)
**Rationale:** Additive `model.py` grammar change with no dependency on (1)-(2).
**Delivers:** `LESSON` section + `LESSON-REF`; minimal `itembank.json` schema + `itembank config` printer.
**Avoids:** the `LESSON-REF`-to-nonexistent-`LESSON` gap — must fail at `lint` time with an actionable message, not render-time `KeyError`.

### Phase 4: Hint Ladder + Cursor-Hold + Feedback-Policy-Per-Mode
**Rationale:** Depends on (1) for evidence-backed `hints_used`/tier tracking and (3) for tier-0 lesson pointers. Largest differentiator and where the revised Core Value's enforcement mechanism must be built.
**Delivers:** tiers 0-5 over authored fields; `submit` holds the cursor on wrong answers; `hint` command; `report` distinguishing right-at-tier-1 from right-at-tier-4; feedback policy as a session-mode property (drill reveals immediately, practice ladders with a held cursor, diagnostic/exam withhold until end), recorded in evidence so a "correct" is mode-attributable.
**Avoids:** gameability by rapid wrong-submission spam — gate tier advancement on a genuine second attempt; make hint-tier-reached a visible `/report` field.

### Phase 5: Model Adapter Interface + Tier-Gate Enforcement (parallel-eligible with Phase 4, gated only by Phase 1)
**Rationale:** This is the phase most changed by PROJECT.md's revision — the model now sees the key/rationale, so the adapter layer must itself enforce the tier gate the runtime decided, checking and dropping any model output that reaches past the unlocked tier before it renders. No research file designed this mechanism; expect original design work here.
**Delivers:** `ModelAdapter` ABC; concrete Claude Code/Codex (subprocess) and OpenAI-compatible (urllib, hosted-or-local as one code path) implementations; `short` rubric marking with `review_state: pending` until explicit accept; hint-tier output validation/stripping; every model interaction logged to evidence.
**Avoids:** Anti-Pattern 4 (adapter output treated as accepted score) — rubric grades stay `pending` until accepted.
**Network-degrade requirement:** the model layer must go quiet (not block) when unreachable, mirroring `day`'s Anki-unavailable pattern — an explicit acceptance criterion here, not implied.

### Phase 6: `check` Item Type + Code Editor
**Rationale:** Independent of (3)-(5); can start any time after (1) lands. Gives CS/Math lanes any verifier-backed item type at all.
**Delivers:** `subprocess`-based execution (timeout + POSIX `resource` + process-group-safe kill/`taskkill`), `<textarea>`+gutter editor, output normalization before diff.
**Avoids:** Pitfall 5 — the honest security posture must be written into the format `spec` output itself; multi-test-case verification (not a single hardcoded string) is an explicit acceptance criterion.

### Phase 7: One Subject-Invariant Loop (integration)
**Rationale:** Necessarily last among content work — needs `LESSON` (3), hint ladder (4), and `check` (6) all present.
**Delivers:** KaTeX wired into quiz/study/daemon pages; the cross-subject demonstration PROJECT.md names as the point of the milestone.

### Phase 8: Objective Scheduler + Daily Cap
**Rationale:** Depends on (1) for objective attribution and evidence history to select against.
**Delivers:** due-today selection, daily cap extension of `day`'s floor rule, decay flagging groundwork.
**Avoids:** Pitfall 6 — Anki-due and itembank-decay computed from one shared per-render snapshot, shown as two labeled signals, never silently merged; also fixes the flagged Anki-query-per-render performance bottleneck for both consumers at once.

### Phase 9: Trends Control Loop
**Rationale:** Natural continuation of (8); needs weeks of real evidence to be meaningful.
**Delivers:** selection-weight adjustment, live decay flagging, longitudinal `/report` (hint-tier-reached as a first-class visible column).

### Phase 10: Auditor
**Rationale:** Depends on (5) for drafting/extraction and (1) for objective-to-item mapping; loosely coupled to (8)/(9) for weak-objective-pointing refinement.
**Delivers:** syllabus ingest → coverage citation-per-claim → draft → `model.lint()` gate → distractor-quality gate (reused from Phase 6) → reversible, one-item-per-commit, distinctly-tagged writes. Report-only ships first and stands alone; draft-and-approve next; full autonomy last, gated behind the second quality check existing.
**Avoids:** Pitfalls 2, 3, 4 — all three converge here and must be resolved before autonomy passes report-only.

### Phase 11: Packaging, Settings, Self-Update (largely parallel-eligible throughout)
**Rationale:** Independent of the evidence-side work; cheapest to finish last.
**Delivers:** `.pyz`/`.pyzw` + per-OS launchers; `--app=` window with fallback to a normal tab; self-update with version-monotonicity rejection and side-by-side-versioned-path-then-relaunch (never overwrite the running file); GIFT export; theming polish.
**Avoids:** Pitfall 8 — checksum documented as integrity-only; downgrade rejection is a hard acceptance criterion; the updater never overwrites its own running `.pyz`.

### Phase Ordering Rationale

- Dependency-first, not feature-grouped: evidence spine before everything that reads/writes it is settled across all three content-research files, not re-litigated here.
- Parallel tracks are named explicitly because Pitfall 7 is specifically about false single-critical-path shape; daemon plumbing, LESSON format, settings scaffold, `check`'s core parsing, and the adapter interface can all start before the evidence spine fully closes.
- The auditor is last among new subsystems because it is highest-risk (Pitfalls 2/3/4 concentrate there) and most dependent on everything else already existing and being trustworthy.
- Packaging/updater is scheduled last but not gated on anything else — genuinely independent, can be pulled forward if useful.

### Research Flags

Needs deeper research during planning:
- **Phase 1:** the opaque-ID-vs-content-hash-alias decision is unresolved by research and must be made with full trade-off awareness; NDJSON write-durability under real crash conditions deserves closer study.
- **Phase 5:** the tier-gate-enforcement mechanism has no direct prior-art analog in any research file and needs fresh design, not just adapter plumbing.
- **Phase 10:** the citation-per-coverage-claim contract and distractor-quality gate are both novel mechanisms with no working precedent found in any examined product.

Phases with standard, well-documented patterns (skip research-phase):
- **Phase 2:** stdlib `http.server` route-table pattern, directly confirmed against official docs.
- **Phase 6:** `subprocess`/`resource`/`timeout` mechanics are HIGH-confidence stdlib patterns with known per-OS caveats already enumerated.
- **Phase 11:** `zipapp`, `os.replace()`, GitHub Releases API usage are all HIGH-confidence officially documented mechanics.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified against official docs and direct package inspection; two explicit MEDIUM watch-items (`--app=` switch permanence, `digest` field literal shape) |
| Features | MEDIUM | Cross-verified across official docs, primary-source accounts, and secondary academic summaries; no product hands-on trialed; several single-source claims flagged LOW inline |
| Architecture | HIGH for general patterns (event sourcing, ports-and-adapters, idempotency, sourced to Microsoft/AWS/Stripe references); the itembank-specific synthesis is opinionated judgment grounded in PROJECT.md and the codebase map, not externally validated against a comparable shipped system |
| Pitfalls | MEDIUM for LLM-content-quality and content-addressing/evidence-reset findings (peer-reviewed/directly analogous prior art); LOW for scheduling-conflict, migration, self-updater, and scope-failure claims (community/issue-tracker sources), triangulated against this codebase's own documented concerns |

**Overall confidence:** MEDIUM-HIGH. Mechanical/technical recommendations are solid; softer claims carry real but bounded uncertainty and are flagged rather than laundered into fact.

### Gaps to Address

- **Opaque-ID vs. content-hash-as-ID decision:** not resolved by research — must be an explicit choice in Phase 1 planning, with "edit an item post-lint, confirm evidence still resolves" as an acceptance test regardless of which is chosen.
- **Tier-gate enforcement mechanism (post-revision):** no research file addresses how to validate/strip model-generated hint text against an unlocked tier boundary — needs original design work in Phase 5.
- **GitHub asset `digest` field exact format:** confirm the literal shape against one real API response before writing the updater's parser; fall back to `SHA256SUMS.txt` if it surprises.
- **Windows memory/CPU rlimit parity:** explicitly deferred as a documented gap (`ctypes` Job Objects) — decide in Phase 6 whether to ship the asymmetry documented (recommended for v1) or build the Job Object path.
- **`--app=` Chromium switch long-term stability:** MEDIUM confidence, community-documented only — the daemon must work in an ordinary browser tab as baseline; test this non-regression explicitly in Phase 11.
- **Hosted-model network-degrade behavior:** PROJECT.md's revision makes this a hard requirement, but no research file stress-tested what "the model layer goes quiet" looks like in code (timeout value, retry policy, UI signal) — needs concretization in Phase 5 planning.

## Sources

### Primary (HIGH confidence)
- `docs.python.org` — `zipapp`, `resource`, `http.server` official stdlib docs
- `katex.org/docs/browser.html`, `github.com/KaTeX/KaTeX` releases, `unpkg.com` package listing
- `code.claude.com/docs/en/headless`, `developers.openai.com/codex/noninteractive`, `docs.ollama.com/api/openai-compatibility`
- Microsoft Learn / AWS Prescriptive Guidance — Event Sourcing pattern reference architectures
- `docs.stripe.com/api/idempotent_requests` — canonical idempotency pattern
- This project's own `.planning/codebase/CONCERNS.md` and `ARCHITECTURE.md`

### Secondary (MEDIUM confidence)
- `academic.oup.com`, `link.springer.com`, `frontiersin.org`, `nature.com` — peer-reviewed/near-peer-reviewed findings on AI-generated MCQ item quality and automation bias
- `arxiv.org` papers on LLM calibration/confidence and curriculum-standard tagging accuracy
- `mike.place`, `code.brettchalupa.com`, Andy Matuschak's notes — Execute Program design details
- `docs.prairielearn.com` — homework/exam variant-mode confirmation
- `borretti.me/article/hashcards` — directly analogous prior-art confirming the content-hash-resets-history trade-off

### Tertiary (LOW confidence)
- Community Chromium switch reference (`peter.sh`) for `--app=`
- Medium/blog commentary on Duolingo engagement criticism, agent approval fatigue
- Anki/Rails/EF Core issue-tracker threads on identifier-change and scheduling-conflict failure modes

---
*Research completed: 2026-08-05*
*Ready for roadmap: yes*
