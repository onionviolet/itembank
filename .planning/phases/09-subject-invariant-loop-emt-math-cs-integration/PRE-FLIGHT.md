# PRE-FLIGHT — Phase 9 (09-subject-invariant-loop-emt-math-cs-integration)

**Status:** BLOCKED — confirmed against current code, exactly as stated. Phase 9 must **not** execute.
**Blocking gates:** Phase 5 (code entirely absent) and Phase 6 (formally open: 06-02 executed in code but never summarized/closed).
**Prepared:** 2026-08-11 (code-truth audit, not a re-plan; no code changed, no source committed).
**Audit method:** each of 09-01..09-05 was read, and every interface/artifact it claims to consume was checked against the working tree (`model.py`, `runtime.py`, `evidence.py`, `surfaces/*`, `schemas/*`, `build.py`, `resources.py`, `tests/*`, `.planning/*`). Precondition roundtrips were executed.

---

## 1. What is already true in code (Phase 9's verified foundation)

| Claim made by a 09 plan | Verified state (file:line) | Verdict |
|---|---|---|
| Phase 3 supplies `model.parse_lesson` | `model.py:173` `def parse_lesson(bank_path)` | ✅ present |
| Phase 3 supplies `surfaces.lesson.render_markdown` | `surfaces/lesson.py:827` `def render_markdown(text, ctx=None)` | ✅ present |
| Phase 3 supplies `lesson_page` + `/lesson/<bank>` + `itembank lesson` | `surfaces/lesson.py:915`; `surfaces/daemon.py:77` `LESSON_GET_RE`; `surfaces/cli.py:731` | ✅ present |
| Phase 3 fenced info strings survive as sanitized `language-*` classes | `surfaces/lesson.py:514` (`<code class="language-%s">`) | ✅ present (the 09-04/09-05 seam) |
| Phase 3 tables are semantic (D-12/D-13 base) | `surfaces/lesson.py:572` `_table_html` → `:590` `<div class="scroll"><table><thead>…<tbody>…` | ✅ present; 09-01 only adds assertions/narrow-width hardening |
| Phase 6 supplies `runtime.teaching_transition(session, q, action, evidence_state=None)` | `runtime.py:540` (exact signature; sole policy path, `kind` in submit/hint/stumped) | ✅ present |
| Phase 6 session seam: `SESSION_VERSION`, `SESSION_UPGRADES`, `upgrade_session`, `session_view` | `runtime.py:28` (`SESSION_VERSION = 2`), `:147`, `:152`, `:196` | ✅ present — 09-01 advances v2 → v3 by exactly one |
| Phase 6 supplies the `surfaces.session` action adapter (`do_action`/`do_hint`) | `surfaces/session.py:235` `do_action(session_file, action, confidence=None, renderer_meta=None)`, `:216` `do_hint`, `:268` calls `teaching_transition`; CLI `hint` (`cli.py:644`); daemon `/api/hint` (`daemon.py:109`) | ✅ present (all 06-02 deliverables exist in code) |
| `evidence.subject_of(objective)` is the one namespaced extractor | `evidence.py:316` | ✅ present — reuse, never re-implement (D-04) |
| `schemas/session.schema.json` is v2 with `teaching_state` (Phase 6) | `schemas/session.schema.json:6` (`x-itembank-version: 2`), `:64` `teaching_state`; type enum `mc/multi/table/dnd/build/short` (`:139`) | ✅ present; v3 adds the nullable `subject_profile` slot |
| `surfaces.settings.load_settings` / `defaults_from_schema` / `merge_over_defaults` | `surfaces/settings.py:114`, `:79`, `:93`; `THIS_PHASE = 7` (`:30`, 09-02 advances to 9) | ✅ present |
| Settings schema conventions 09-02 relies on (closed object, `required`, `x-itembank-phase`) | `schemas/settings.schema.json:8` `additionalProperties: false`, `:9` `required`, per-key `x-itembank-phase` | ✅ present |
| `build.STAGE_DIRS` explicit allowlist; `resources.read_bytes` sole reader | `build.py:33` `STAGE_FILES`, `:37` `STAGE_DIRS = ("surfaces","schemas","styles","fonts")`, `:66` `stage()`; `resources.py:33` | ✅ present — 09-04 adds `vendor` to `STAGE_DIRS` (research's `STAGE_DIRS = ("surfaces","schemas")` claim at `09-RESEARCH.md:230` is stale but harmless) |
| `tests/hint_roundtrip.py`, `lesson_roundtrip.py`, `scoring_roundtrip.py`, `config_roundtrip.py`, `packaging_roundtrip.py` exist | all five files present | ✅ present |
| 09-03's automated gate references (`Package Legitimacy Audit`, `katex`, `SUS`) | `09-RESEARCH.md:112`, `:122` (`katex` flagged `[SUS]` on recency) | ✅ present — 09-03's verify command will pass when run |
| 09-01 read_first references (Pattern 1/4, Pitfall 3, Validation Architecture) | `09-RESEARCH.md:167`, `:187`, `:246`, `:329` | ✅ present |
| 09-02's `lesson_layout` fold (ROADMAP ruling 7 / 03.1 D-04) | already folded into `09-02-PLAN.md:31,83,108` (`"separate" | "inline"`; EMT/Math `separate`, CS `inline`); `03.1-CONTEXT.md:23` confirms the fold target | ✅ resolved pre-execution |

**Precondition roundtrips executed (all exit 0):** `tests/hint_roundtrip.py`, `tests/lesson_roundtrip.py`, `tests/scoring_roundtrip.py`, `tests/config_roundtrip.py`, `tests/packaging_roundtrip.py`.

---

## 2. Blocking gates — exact state

### Phase 5 (hard code blocker — nothing exists yet)
- `.planning/phases/05-*` contains **plans only, zero SUMMARY files**. ROADMAP `05-01`..`05-07` all `[ ]` (ROADMAP:483–501).
- **`runner.py` does not exist.** **`tests/check_roundtrip.py` does not exist.**
- Item types shipped by `model.py` are only `mc, multi, table, build, dnd, short` (SPEC at `model.py:1407–1434`; `session.schema.json:139`). **`[TYPE: check]` is not parsed, not scored, not in any schema.**
- No `check` settings group (`check.timeout_seconds/max_output_bytes/languages/allow_lan`) in `schemas/settings.schema.json` or `itembank.json`.
- No daemon check-execution gates (`POST /quiz/<stem>/answer` check branch, `/api/submit` check branch, LAN refusal).
- ROADMAP:468: `05-05` must be **rewritten to the CM6 plan** before Phase 5 execution (a Phase 5-internal gate, but it affects the vendoring convention 09-04 may inherit).

### Phase 6 (process gate open — code is actually present)
- `06-01-SUMMARY.md` exists (commit `5183927`); **`06-02-SUMMARY.md` does not exist**, and ROADMAP `06-01`/`06-02` remain `[ ]` (ROADMAP:538–542). The Phase 6 phase gate (summary + validation) is open.
- **However, every 06-02 deliverable already exists in code and is green**: `session.do_action`/`do_hint` (`surfaces/session.py:235/216`), `itembank hint` (`cli.py:644`), `POST /api/hint` (`daemon.py:109`), and `tests/hint_roundtrip.py` passes. So Phase 6 is a **bookkeeping blocker, not a code blocker** for 09-01/09-05.

---

## 3. Which plan steps depend on Phase 5 / Phase 6 specifics (the unblock list)

### 09-01 (wave 1, `depends_on: []`) — **no Phase 5 dependency; Phase 6 dependency is code-satisfied**
| Step | Phase-5/6 specific it needs | Where referenced |
|---|---|---|
| 09-01 T1 precondition | Phase 3 + Phase 6 only: `lesson_roundtrip.py`, `teaching_transition`, `hint_roundtrip.py` | `09-01-PLAN.md:104` — all ✅ today |
| 09-01 T1/T2 `DEFAULT_PROFILE` | "established non-`check` item types" (`mc/multi/table/build/dnd/short`) — deliberately excludes `check` | `09-01-PLAN.md:124,159` — no Phase 5 need |
| 09-01 T1 session upgrade | Phase 6's `SESSION_VERSION` (2) to advance to 3 | `runtime.py:28` — ✅ |
| 09-01 T1 EMT tracer | Phase 6 `teaching_transition` + `surfaces.session` adapter as the only action path | `09-01-PLAN.md:119,128` — ✅ |
| **09-01 does not block on Phase 5.** It blocks only on Phase 6's *gate* closing (summary/validation), not on any missing code. | | |

### 09-02 (wave 2, `depends_on: 09-01`) — **one real Phase 5 coupling, currently unlabeled**
| Step | Phase-5/6 specific it needs | Where referenced |
|---|---|---|
| 09-02 T1 CS registry row | `[TYPE: check]` must be a legal type and **Phase 5's check verifier id** must exist as a named verifier | `09-02-PLAN.md:110` ("only CS permits `check`… Phase 5's check verifier id for CS") |
| 09-02 T1 verification | `python tests/config_roundtrip.py` (exists ✅) | `09-02-PLAN.md:115` |
| 09-02 T1 `THIS_PHASE` → 9 | `surfaces/settings.py:30` (currently 7) | `09-02-PLAN.md:112` — no Phase 5 need |
| ⚠️ **Catch:** the plans declare no Phase 5 dependency for 09-02, but the CS profile cannot validate (`check` unknown type / unknown verifier id) until Phase 5 lands or until 09-02 defines the id and Phase 5 matches it. **Record a cross-phase contract now:** Phase 5 must name its check verifier/type exactly `check` (or 09-02's id must be reconciled at Phase 5 execution). | | |

### 09-03 (wave 2, `depends_on: []`) — **no Phase 5/6 dependency**
Metadata-only human checkpoint (KaTeX approval). Consumes `09-RESEARCH.md` (✅) and `build.py` allowlist (✅). The automated gate already has its inputs (`09-RESEARCH.md:112/122`).

### 09-04 (wave 3, `depends_on: 09-02 + 09-03`) — **no Phase 5/6 code dependency**
- Consumes 09-01/09-02 `subjects.session_profile()` + `lesson.math`, 09-03 approval, `build.STAGE_DIRS`, `resources.read_bytes`, `tests/packaging_roundtrip.py` — all verified present (Section 1).
- Read_first mentions "CSP/security headers" and "existing static-resource handlers" in the daemon — **neither exists today** (no `Content-Security-Policy` anywhere in the repo; no `/assets/` handler; `daemon.py` has no static route). Non-blocking (09-04 builds the first one), but the plan's read_first is optimistic; expect to *add* these, not extend them.

### 09-05 (wave 4, `depends_on: 09-02 + 09-04`) — **the heavy Phase 5 consumer; every Phase 5 item below is absent today**
| Step | Phase-5/6 specific it needs | Where referenced |
|---|---|---|
| 09-05 T1 precondition | `runner.py`, `tests/check_roundtrip.py`, the `check` settings group, Phase 5 LAN refusal tests — **all missing** | `09-05-PLAN.md:126` |
| 09-05 T1 extract `run_source()` | `runner.run_cases(q, source, timeout_seconds, max_output_bytes, languages)` + `runner.UnknownLanguage` + per-case spawn/drain/timeout/cap/tree-cleanup | `09-05-PLAN.md:103–104,144` (Phase 5's own contract: `05-01-PLAN.md:136,142,444`; settings bounds `05-03-PLAN.md:104–107,154–159`) |
| 09-05 T1 factor `execution_refusal()` | the two Phase 5 daemon check-submit LAN/language gates (`/quiz/<stem>/answer` + `/api/submit`), **keeping their copy byte-for-behavior** | `09-05-PLAN.md:146`; Phase 5 gates in `05-03-PLAN.md:315–317,405`; locked refusal copy in `05-UI-SPEC.md:239` |
| 09-05 T1 settings bounds | `check.timeout_seconds` (default 5), `check.max_output_bytes` (default 65536), `check.languages`, `check.allow_lan` (default false) | `09-05-PLAN.md:132,146`; Phase 5 defaults `05-03-PLAN.md:104–107` |
| 09-05 T3 CS fixture | a real `[TYPE: check]` item + check verifier + runnable `python` fence grammar | `09-05-PLAN.md:217` |
| 09-05 T3 verification | `python tests/check_roundtrip.py` (Phase 5's suite) | `09-05-PLAN.md:224` |
| 09-05 T2 Phase 6 part | `session.do_action()`/`do_hint()` + stored snapshot resume | `09-05-PLAN.md:170–171` — ✅ present |
| 09-05 T2 clients | `itembank start/lesson` (`cli.py:580/731`), `/api/start` (`daemon.py:106`), `/lesson/<stem>` (`daemon.py:77`), `session_index` (`daemon.py:1464`) — all ✅ present; `--profile`/`{profile:}` params are 09-05 additions | | |

---

## 4. Instant-execution checklist (run when Phase 5 lands and Phase 6 closes)

1. **Phase 5 done means all of:** `runner.py` with `run_cases`+`run_source`-extractable internals and `UnknownLanguage`; `[TYPE: check]` parsed/scored/typed (model SPEC + `session.schema.json` enum + response schema); `check.*` settings group (schema + `itembank.json`); daemon check branches + `check.allow_lan` refusal on both submit routes; `tests/check_roundtrip.py` green; a **named check verifier id** (see 09-02 coupling above).
2. **Phase 6 done means:** `06-02-SUMMARY.md` written and Phase 6 marked complete (code is already present and `tests/hint_roundtrip.py` passes).
3. **Then, before 09-01, one planning decision (Section 5):** resolve the `## SCENARIO` (and numeric-equivalence/search/style) coverage gap — fold into a new plan or explicitly defer in ROADMAP. Otherwise "instant execution" silently ships a Phase 9 that does not meet ROADMAP criteria 7–9, 11, 14.
4. Gate commands to re-run at that point (current baseline all exit 0, except the two new suites):
   `python tests/hint_roundtrip.py && python tests/lesson_roundtrip.py && python tests/scoring_roundtrip.py && python tests/config_roundtrip.py && python tests/packaging_roundtrip.py && python tests/check_roundtrip.py && python tests/daemon_roundtrip.py`

---

## 5. ⚠️ SCENARIO and other uncovered ROADMAP criteria (planning gap, not code gap)

The request called out the **SCENARIO staging in 09-02..04** — verified result: **it is not there.**

- ROADMAP owes Phase 9 **`## SCENARIO`** — Success Criterion 7 ("a phased container in which **the runtime stages the information reveal**") and Criterion 12 (R3.2: ordered `[STAGE:]` blocks, closed two-value advance `on-ack`/`on-item`, reveal position **derived from replayed evidence**, five lint codes, zero new item types, zero scorer change). ROADMAP:316,739,744.
- 09-02 stages only the **subject-profile registry** (data), 09-03 the **KaTeX supply-chain gate**, 09-04 the **vendored math assets** — none stages the SCENARIO container.
- Grep across the whole phase directory: **zero** `SCENARIO`/`[STAGE:]` matches in `09-01..09-05-PLAN.md`, `09-VALIDATION.md`, or `09-UI-SPEC.md`. `model.py` has no `SCENARIO`/`STAGE:`/`lesson_layout` support. Nothing in the plans will create it.
- Downstream consumers already bind to it: `styles/case-narrative.md` (shipped in 3.1) declares the Phase 9 SCENARIO dependency (`03.1-04-SUMMARY.md:152`), `03.1-UI-SPEC.md:857` binds the reveal renderer, `06.2-UI-SPEC.md:19` expects Phase 9 to reuse its §6 reveal renderer, `13-UI-SPEC.md:676` (C2) treats the SCENARIO surface as Phase 9-owned.
- Also uncovered by 09-01..05, yet listed as Phase 9 criteria: **8/14** (WeBWorK-style random-point numeric equivalence, seed derived from `content_hash`), **9** (grep-grade local search route), **11** (`math-worked`/`math-explore` — `styles/` ships `house, expository, worked-example, checked-prose, artifact-first, case-narrative`; no `math-worked`). Criterion 13 (`lesson_layout`) is the one research-derived criterion that **is** folded in (09-02).

**Decision needed before execution** (do not silently skip): fold SCENARIO into a new plan (e.g. `09-06`, parser/lint in `model.py` + runtime-derived reveal in `runtime.py`/reader — fits the "one parser, runtime decides" invariants), or explicitly re-scope ROADMAP's Phase 9 criteria. Either way, `09-VALIDATION.md`'s traceability table has no row for it today.

---

## 6. Residual risks / notes (non-blocking)

- **Working tree hygiene:** `build.py` and `evidence.py` show as modified but the diffs are line-ending-only churn (CRLF/LF), no semantic drift. `tmp_*.patch` scratch files and `.planning/research/.cache/…json` are untracked leftovers — do not copy them into Phase 9 work. **Nothing here was changed by this audit.**
- **Verifier-id naming (cross-phase contract):** neither "runtime verifier id" nor "check verifier id" exists in code (no `verifier` symbol anywhere in `runtime.py`/`model.py`). 09-01 mints the id concept in `subjects.py`; 09-02's CS row references "Phase 5's check verifier id" — pin the id string (proposal: `check`) in the Phase 5 execution notes so the registry and the Phase 5 scorer agree.
- **09-04 daemon read_first** expects CSP/static-asset handlers that don't exist yet; treat them as 09-04's own additions.
- **Phase 6 gate:** only bookkeeping (`06-02-SUMMARY.md` + validation row) — do not wait on code.
