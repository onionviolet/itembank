---
phase: 02-daemon-consolidation-settings-foundation
verified: 2026-08-07T19:26:45Z
status: passed
score: 9/9 must-haves verified
human_confirmed: 2026-08-08 — all 3 backstop items (LAN phone reachability, UI-at-scale rendering, concurrent config-set torn-file check) confirmed passing by user report; not independently re-derived by this session
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Start `itembank daemon <dir> --lan`, note the printed phone URL, open it in a browser on a phone joined to the same wifi, and confirm the index and a quiz page render."
    expected: "The page renders on the second device, proving the bind actually widened beyond loopback and is reachable across the network, not just locally addressable."
    why_human: "A loopback-only automated test can prove the socket bound 0.0.0.0 and that this machine can reach it via its own LAN IP, but it cannot prove a second physical device on the wifi can. 02-06-SUMMARY.md records this explicitly as an outstanding manual-only verification (D5, `human_judgment: true`, status `unknown`) — it has not been exercised in this project session."
  - test: "Open `/` and `/report?session=<id>` in a real browser at various window widths and with 20+ scanned banks/plans, and with a session carrying 10+ pending short items; confirm the 8-point spacing scale, the four-font-size/two-weight typography, the 60/30/10 color split, and that rows/objective lists wrap and scroll with the page rather than truncating or clipping."
    expected: "Visual rendering matches 02-UI-SPEC.md's Spacing/Typography/Color contract at scale."
    why_human: "Automated checks in this phase only confirm the required copy strings and the absence of `nowrap`/`text-overflow` CSS declarations — they do not render the page. 02-01-SUMMARY.md (D7) and 02-05-SUMMARY.md (D8) both explicitly mark this `human_judgment: true` / carried as a backstop, and no fixture in the repo currently has 10+ pending short items to exercise the overflow case."
  - test: "Run two `itembank config set` invocations against the same `itembank.json` at effectively the same instant (e.g. two shells launched together) and confirm the file never ends up torn or unparseable, and that the surviving value is one of the two writers' values (last-writer-wins), not a hybrid."
    expected: "No torn/corrupt file under concurrent writes; at most one writer's change is silently dropped."
    why_human: "This must-have is explicitly declared `verification: backstop` in 02-03-PLAN.md's frontmatter. It is currently accepted architecturally (tmp-then-`os.replace()` makes a torn file impossible by construction, per `runtime.write_session`'s existing pattern) but is not exercised by a concurrency stress test — 02-03-SUMMARY.md's own coverage table (D11) marks this `human_judgment: true`."
---

# Phase 02: Daemon Consolidation & Settings Foundation Verification Report

**Phase Goal:** The learner opens one process on one port for everything — sitting, studying, the day
view, reports, and settings — and every capability in it also has a CLI command.
**Verified:** 2026-08-07T19:26:45Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

Truths 1–4 are the ROADMAP.md Success Criteria for this phase (the contract); truths 5–9 are
representative must-haves drawn from the six plans' frontmatter, chosen because they are the ones a
stub or a silently-reverted change would most plausibly hide behind (no second scorer, no path
traversal, no daemon-killing routine error, the LAN-reachability half of SC2, and the visual/
concurrency backstops the plans themselves declined to automate).

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Starting the daemon once serves `/`, `/quiz/<bank>`, `/study/<bank>`, `/report`, `/api/*`, and the day view from one port | ✓ VERIFIED | Live smoke test against a temp directory with `fixtures/sample_bank.md` + `fixtures/sample_plan.md`: single `itembank daemon . --port 0` process answered `GET /` (200, links present), `GET /quiz/sample_bank` (200), `GET /study/sample_bank` (200), `GET /day/sample_plan` (200), `GET /__itembank__` (`{"itembank": true}`), `POST /api/start` (200, valid session JSON), `GET /report` (404 documented copy, no session given) — all from one process on one port. `tests/daemon_roundtrip.py` (46 checks) also passes; `route/cli inventory` check confirms all 14 registered routes. |
| 2a | Starting the daemon a second time does not fight over the port — it detects and attaches instead of double-binding | ✓ VERIFIED | Live smoke test: second `itembank daemon` invocation on the already-held port printed `itembank is already running at http://127.0.0.1:1046/` and exited without a second bind. `tests/daemon_roundtrip.py#check_startup_second_attaches` and `#check_probe_*` pass. 02-06 also found and fixed a real bug (`Daemon.allow_reuse_address=True` silently defeated detect-and-attach on Windows) before this behavior held. |
| 2b | `--lan` reaches a phone on the same wifi | ⚠️ Backstop, not exercised — see Human Verification | Automated coverage proves the bind widens to `0.0.0.0`, the banner prints a `lan_address()`-derived phone line, and this machine can reach its own LAN IP (`check_startup_lan_binds_all`). It does not and structurally cannot prove a second physical device can reach it. 02-06-SUMMARY.md's own coverage table (D5) records this as `human_judgment: true`, status `unknown`, "still outstanding." |
| 3 | For every route exercised in a manual pass, an equivalent CLI command exists reaching the same runtime call | ✓ VERIFIED | `set(daemon.ROUTE_CLI) == set(e[:2] for e in daemon.ROUTES)` holds for all 14 routes (checked live). Parity is proven, not just claimed: `check_api_cli_parity` (evidence events from an `/api/*` sitting match a CLI sitting), `check_study_cmd_matches_study_page` (byte-equal output), `check_report_matches_command` (`/report` numbers match `session.do_report`). |
| 4 | `itembank config` prints the settings schema like `spec`; an invalid value is rejected with a named error | ✓ VERIFIED | Live run of `itembank config` confirmed the human table (7 top-level keys, type/range/default/current/status columns, "inert — read from phase N" for 6 of 7, "read by this phase" for `daemon`). `tests/config_roundtrip.py` passes 14 checks including all 6 `SETTINGS_CODES` reachable and exact boundary values. |
| 5 | No second scorer or evidence writer exists in the daemon — every verdict comes from `runtime.score_response()`/`evidence.append_event()` via `quiz.record_answer()`/`session.do_submit()` | ✓ VERIFIED | Source-inspection acceptance criteria (`'canonical_response' not in src and 'canonical_key' not in src`) and `tests/daemon_roundtrip.py`'s answer-scoring and API-sitting checks pass; `POST /api/submit` observed live returning a scored item from `runtime`'s own item selection. |
| 6 | A client-supplied `session`/`bank` value naming a filesystem path (traversal, absolute path) is rejected and reaches no file | ✓ VERIFIED | `tests/daemon_roundtrip.py#check_api_start_traversal`, `#check_api_reject_path_fields`, `#check_report_not_found` (parent-directory `session` value) all pass; directory-snapshot-before/after assertions confirm no file/dir is created. |
| 7 | A routine CLI-style error (session already complete, bad objective, malformed session) returns 4xx and leaves the daemon serving every other route | ✓ VERIFIED | `check_api_survives_routine_error` asserts `GET /` still returns 200 on the same process after a rejected `/api/submit`; source inspection confirms `except SystemExit` paired with `except Exception` on every reused command-body call site (`SystemExit` derives from `BaseException`, not `Exception`). |
| 8 | The `/` index and `/report` page render legibly at scale (20+ rows, 10+ pending items) and match 02-UI-SPEC.md's spacing/typography/color contract | ⚠️ Backstop, not exercised — see Human Verification | Automated checks confirm required copy strings and the absence of `nowrap`/`text-overflow` CSS, but no browser rendering was performed. 02-01-SUMMARY.md (D7) and 02-05-SUMMARY.md (D8) both explicitly carry this as a human/UAT item. |
| 9 | Concurrent `itembank config set` writes never produce a torn/unparseable `itembank.json` | ⚠️ Backstop, not exercised — see Human Verification | Declared `verification: backstop` in 02-03-PLAN.md's frontmatter; accepted architecturally via `write_settings()`'s tmp-then-`os.replace()` (the same primitive `runtime.write_session` already relies on), but not exercised by a concurrency test. |

**Score:** 6/9 truths verified (3 explicitly backstop/human-only, none failed)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `surfaces/daemon.py` | One route table, one Handler, `probe`/`start_server`, all route handlers | ✓ VERIFIED | Exists, 14 registered routes, `probe`/`start_server`/`serve_scoped`/`ALL_INTERFACES` all present and exercised live |
| `surfaces/settings.py` | `cmd_config`, `load_settings`/`write_settings`, `SETTINGS_CODES`, `classify_error` | ✓ VERIFIED | Exists; `itembank config`/`config schema`/`config set` all confirmed live |
| `schemas/settings.schema.json` | Published schema for `itembank.json`, all 7 keys typed/ranged/defaulted/phase-annotated | ✓ VERIFIED | `itembank config schema` output is the file verbatim (tested); `itembank.json` validates clean against it |
| `itembank.json` | Settings file at repo root, every key at schema default | ✓ VERIFIED | Present at repo root; `daemon.lan` is `false` (confirmed) |
| `surfaces/quiz.py`, `surfaces/study.py`, `surfaces/day.py` | No `do_GET`/`do_POST` — daemon is the sole HTTP mechanism | ✓ VERIFIED | Confirmed via source-inspection acceptance criteria in 02-02; `surfaces/daemon.py` is the only module defining request handlers |
| `surfaces/session.py` | `do_start/do_next/do_submit/do_report` factored out, callable by both CLI and daemon | ✓ VERIFIED | Exists; CLI/daemon parity test (`check_api_cli_parity`) passes |
| `tests/daemon_roundtrip.py` | Wave-0 integration harness covering the whole phase | ✓ VERIFIED | 46 checks, all pass live |
| `tests/config_roundtrip.py` | DEL-04/DEL-05 coverage | ✓ VERIFIED | 14 checks, all pass live |
| `surfaces/quiz_page.py` | Bank-scoped `__POST__` placeholder | ✓ VERIFIED (functionally) — ⚠️ carries an unrelated security defect | Present and wired correctly for its stated purpose (one process serving several banks); see Known Open Issue (CR-01) below for an unrelated client-side escaping defect in the same file |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `surfaces/daemon.py` (quiz answer route) | `runtime.py` | `score_response()` reached only through `quiz.record_answer()` | ✓ WIRED | Confirmed by source-inspection assertion and a live `POST /api/start`→scored-item round trip |
| `surfaces/daemon.py` (quiz answer route) | `evidence.py` | `append_event()` reached only through `quiz.record_answer()`/`session.do_submit()` | ✓ WIRED | Confirmed by `check_two_bank_isolation`, `check_api_sitting` (evidence read back via `evidence.live_events`) |
| `surfaces/daemon.py` | `surfaces/study.py`, `surfaces/day.py` | `study_page()`, `day_render()`, `apply_day_post()` | ✓ WIRED | `check_study_cmd_matches_study_page` proves byte-equality between the CLI's written file and the daemon's served page |
| `surfaces/daemon.py` (`/api/*`) | `surfaces/session.py` | `session.do_start/do_next/do_submit/do_report` | ✓ WIRED | `check_api_cli_parity` compares recorded evidence events from an API-driven sitting and a CLI-driven sitting on the same seed |
| `surfaces/daemon.py` (`/report`) | `runtime.py` / `surfaces/session.py` | `session.do_report()` → `runtime.session_summary()` | ✓ WIRED | `check_report_matches_command` compares three named numeric fields between the page and the command |
| `surfaces/cli.py` | `surfaces/settings.py` | `cmd_config` dispatch | ✓ WIRED | Confirmed live: `itembank config` invokes `cmd_config` and prints the expected table |
| `surfaces/daemon.py` | `surfaces/settings.py` | `cmd_daemon` reads `daemon.port`/`daemon.lan` via `load_settings()` | ✓ WIRED | `check_settings_driven_port` passes; plan acceptance criterion confirms the pattern |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| One daemon serves index + quiz + study + day + api + report on one port | Live daemon started on a temp dir; `curl` against 6 distinct routes | All returned expected status/body (200s, correct JSON marker, documented 404 copy) | ✓ PASS |
| Second daemon on the same port attaches rather than double-binding | Live second `itembank daemon . --port <held-port>` invocation | Printed `itembank is already running at http://127.0.0.1:<port>/` and exited cleanly | ✓ PASS |
| `itembank config` prints the live schema table | `python itembank.py config` | 7 top-level keys, correct type/range/default columns, `daemon` marked "read by this phase," the other 6 marked "inert" | ✓ PASS |
| `itembank daemon --help` documents `--port`/`--lan`/`--no-open`/`--force` | `python itembank.py daemon --help` | All four flags present with expected help text | ✓ PASS |
| Full test suite | `for t in tests/*.py; do python "$t" || exit 1; done` | All 12 test files pass, including `daemon_roundtrip.py` (46 checks), `config_roundtrip.py` (14 checks), `serve_roundtrip.py`, `day_roundtrip.py`, `evidence_roundtrip.py`, `agent_roundtrip.py` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| SURF-01 | 02-01, 02-02, 02-04, 02-05 | One daemon serves every surface on one port | ✓ SATISFIED | Live smoke test hit all named routes on one port; 46 automated checks pass |
| SURF-02 | *(not this phase — Phase 4)* | Browser holds no key, is a plain JSON API client | — Out of scope | Correctly not claimed by this phase; REQUIREMENTS.md maps it to Phase 4 |
| SURF-03 | 02-06 | Daemon doesn't fight over the port twice; `--lan` reaches a phone | ✓ SATISFIED (port contention) / ⚠️ backstop (cross-device reach) | Detect-and-attach proven live and by 8 automated startup-case checks; the phone-reachability half is explicitly recorded as an outstanding manual check in 02-06-SUMMARY.md |
| SURF-04 | 02-01 through 02-06 | Every capability has both a route and a CLI command over one runtime | ✓ SATISFIED | `ROUTE_CLI` inventory equality holds across all 14 routes; multiple parity tests prove same-runtime-call, not two implementations |
| DEL-04 | 02-03 | One documented settings file with 6 named keys plus daemon's own settings | ✓ SATISFIED | `itembank.json` + `schemas/settings.schema.json` confirmed live, 7 keys, typed/ranged/defaulted/phase-annotated |
| DEL-05 | 02-03 | `itembank config` prints the schema like `spec`; invalid values rejected by name | ✓ SATISFIED | Confirmed live; dotted `SETTINGS_CODES` namespace, boundary-value tests pass |

**No orphaned requirements.** REQUIREMENTS.md's traceability table maps exactly SURF-01, SURF-03, SURF-04, DEL-04, DEL-05 to Phase 2 — identical to the phase requirement IDs given for this verification, and identical to the union of `requirements:` fields declared across the six plans' frontmatter.

### Anti-Patterns Found

No blocker-level anti-patterns (no `TBD`/`FIXME`/`XXX` debt markers, no placeholder/stub returns) found in any file this phase modified (`surfaces/daemon.py`, `surfaces/quiz.py`, `surfaces/quiz_page.py`, `surfaces/cli.py`, `surfaces/study.py`, `surfaces/day.py`, `surfaces/session.py`, `surfaces/settings.py`, `schema_validate.py`).

### Known Open Issue (from Code Review — advisory, non-blocking)

**CR-01 (Critical, per 02-REVIEW.md): `surfaces/quiz_page.py`'s client-side `esc()` helper does not escape HTML — stored XSS via bank content.**

Confirmed directly against source during this verification:

```
surfaces/quiz_page.py:125:  const esc = s => (s==null?"":String(s));
surfaces/study.py:30:       const CARDS=__DATA__,esc=s=>(s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
```

`quiz_page.py`'s `esc()` is a null-coalescing stringifier only — it performs no `&`/`<`/`>` escaping — yet is used throughout the quiz page everywhere item content (stem, option text, rationale, discriminator, second-best, trap, rubric lines, notes, model answer) is written into `innerHTML`. `study.py`'s `esc()`, in the same phase, correctly escapes all three characters. Any bank content containing HTML markup will execute in the learner's browser via `GET /quiz/<stem>` and `POST /quiz/<stem>/answer`, and the project's own threat model already accepts that item text may originate from third-party or (eventually) model-generated sources not guaranteed markup-free.

This is a **real, present defect** in code this phase shipped and wired into the daemon (`handle_quiz_get`/`handle_quiz_answer`). Per this project's code-review gate, code review is advisory only and does not block phase completion — this phase's automated must-haves and success criteria do not depend on `esc()`'s correctness, so it does not change the `status` determination above. It is recorded here so it is visible in the verification record rather than only in `02-REVIEW.md`, and should be fixed before this surface is exposed under `--lan` to other devices or before item content in the bank format is treated as untrusted (per the review's own recommended fix: match `study.py`'s escaping).

### Human Verification Required

1. **`--lan` cross-device reachability** — Start `itembank daemon <dir> --lan`, open the printed phone URL on a phone on the same wifi, confirm the index and a quiz page render. Explicitly recorded as outstanding in 02-06-SUMMARY.md; cannot be proven by a loopback-only automated test.
2. **Visual/layout conformance to 02-UI-SPEC.md at scale** — `/` with 20+ rows and `/report` with 10+ pending items; confirm spacing/typography/color contract and that content wraps/scrolls rather than truncating or clipping. Carried as an explicit backstop in 02-01 and 02-05.
3. **Concurrent `config set` last-writer-wins behavior** — Confirmed architecturally (atomic `os.replace()`) but not stress-tested. Carried as an explicit backstop in 02-03.

### Gaps Summary

No gaps found — every must-have that can be verified programmatically was verified, both against the automated test suite (which was re-run in full during this verification and passed: 12/12 test files) and against a live, freshly-started daemon process exercised directly with `curl` (not just trusted from SUMMARY.md narration). The phase goal — one process, one port, every surface, every capability with a CLI equivalent — is demonstrably achieved in the codebase.

The reason this report is `human_needed` rather than `passed` is that three of the plans' own declared must-haves are explicit backstops (LAN cross-device reach, visual rendering at scale, concurrent-write behavior) that the plans themselves chose not to automate and that remain genuinely unexercised in this project session — not because anything failed. Additionally, a real, present security defect (CR-01) exists in shipped code; it does not block this phase's completion under this project's advisory-only review gate, but it is flagged here so it is not lost before the next phase exposes this same daemon more widely (Phase 4's SURF-02 work, and any future `--lan` usage).

---

_Verified: 2026-08-07T19:26:45Z_
_Verifier: Claude (gsd-verifier)_
