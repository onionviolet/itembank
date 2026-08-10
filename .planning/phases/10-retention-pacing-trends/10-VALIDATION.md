# Phase 10 Validation Strategy

## Validation posture

Phase 10 is evidence-first and tracer-first. Wave 0 creates `tests/retention_roundtrip.py` before browser work and proves one immutable captured snapshot can drive a due recommendation and surface-neutral report. Plans 10-02 through 10-04 then attach explicit lesson completion, Phase 7 selection, and runtime pacing. Browser work in 10-05 consumes those contracts; 10-06 supplies the cross-surface and human UI gates.

No test may read a real learner bank/log, contact a model provider, require Anki, or create a second parser, scorer, runner, evidence store/writer, selector, report calculator, or settings source.

## Wave and dependency gates

| Gate | Required fact | Plan / command |
|---|---|---|
| Wave 0 | Fixed synthetic UTC/local-day evidence covers retraction, pending/manual settlement, sparse state, and byte-stable provenance. | 10-01 · `python tests/retention_roundtrip.py` |
| Lesson seam | Phase 3 heading/objective resolution exists; explicit completion is versioned and views are read-only. | 10-02 · `python tests/lesson_retention_roundtrip.py` |
| Selector seam | Phase 7 plan 07-06 sole-selector contract exists and remains fixed-seed compatible. | 10-03 · `python tests/selection_retention_roundtrip.py` |
| Pacing seam | Start and submit both enforce live per-subject cap; override is sitting-bound evidence. | 10-04 · `python tests/pacing_roundtrip.py` |
| UI foundation | Phase 4 presentation/day contracts exist; Today/report perform no browser-side derivation. | 10-05 · `python tests/retention_ui_roundtrip.py` |
| Phase gate | One snapshot crosses Today/start/selector/report; all tests and manual widths/accessibility pass. | 10-06 · `python tests/phase10_uat.py` + full suite + checkpoint |

## Requirement-to-test matrix

| Requirement | Observable proof | Focused command | Plan |
|---|---|---|---|
| SCHED-01 | Due objectives and Anki due/new appear separately from one render; all itembank claims share a snapshot. | `python tests/retention_roundtrip.py` and `python tests/retention_ui_roundtrip.py` | 10-01, 10-05 |
| SCHED-02 | Per-subject live local-day cap blocks start/submit; one explicit override expires with the sitting. | `python tests/pacing_roundtrip.py` | 10-04 |
| SCHED-03 | Anki is read-only and separately labeled; zero/populated/unavailable never changes objective state/cap/weight. | `python tests/day_roundtrip.py` and `python tests/retention_ui_roundtrip.py` | 10-04, 10-05 |
| SCHED-04 | Explicit Phase 3 heading completion appends one event and enters a transparent configured review queue; view/scroll does nothing. | `python tests/lesson_retention_roundtrip.py` | 10-02, 10-05 |
| TREND-01 | Weak/due objective gets bounded higher weight in next practice/remediation choice; mastered leaves ordinary rotation with bounded fallback. | `python tests/selection_retention_roundtrip.py` | 10-03 |
| TREND-02 | Subject load comes from captured live evidence and re-cuts with named reason after event/retraction. | `python tests/day_roundtrip.py` | 10-04 |
| TREND-03 | Week report exposes raw accuracy counts, highest/average hint, attempts, pending, last date across CLI/browser parity. | `python tests/retention_roundtrip.py` and `python tests/retention_ui_roundtrip.py` | 10-01, 10-05 |
| TREND-04 | Proven success plus 28 days of silence becomes at-risk with exact observed reason; untouched no-success remains unknown. | `python tests/retention_roundtrip.py` | 10-01 |
| TREND-05 | Every state, row, recommendation, weight and chosen reason references one complete evidence claim. | `python tests/phase10_uat.py` | 10-01, 10-03, 10-06 |

## Deterministic fixture matrix

`tests/retention_roundtrip.py`, `fixtures/lesson_retention_events.jsonl`, and focused integration tests must cover:

| Fixture | Expected state/behavior |
|---|---|
| No evidence | `unknown`; null accuracy/last date; `Not enough evidence yet`; ordinary practice remains available. |
| Three settled, one correct | `weak` and `due`; raw `1/3`; weak component visible. |
| Three recent distinct-day successes above threshold | `mastered`; absent from ordinary rotation while other work exists; bounded fallback remains. |
| Prior accepted success, 27d 23h silence | Not at-risk. |
| Prior accepted success, 28d silence | `at-risk` and due; reason names last proven success and elapsed configured threshold. |
| Pending-only constructed responses | `unknown`; pending count increases pacing attempts; mastery numerator/denominator unchanged. |
| Accepted human mark | Settles the targeted constructed response in the next snapshot. |
| Phase 8 proposal/model event | Never settles completion or mastery and never changes recommendation/weight. |
| Compensating retraction | Target disappears from state, series, cap, completion queue, and counts while raw audit bytes remain. |
| Local-day boundary in two zones | Only events inside the named zone/day count toward the subject cap. |
| Completion event before/at configured review boundary | Future queue date before boundary; `due` with `lesson review` reason at boundary. |
| Anki zero/populated/unavailable | Only the separately labeled Anki text changes; itembank snapshot id and derivation remain byte-identical. |
| Same capture twice | Byte-identical JSON and snapshot id. |
| Append after capture | Existing payload remains internally unchanged; a fresh capture has a new marker. |
| Prior selection map | Each normalized objective value moves no more than configured max step. |
| Exam with/without retention context | Identical chosen items and evidence-neutral choice trace. |

## Evidence claim contract

Every rendered or serialized derived claim must carry or reference the same top-level object:

`{snapshot_id, cutoff, local_day_zone, window, filters, live_event_count, settings_version}`

Tests must assert claim equality across Today card, EvidenceDrawer, cap decision, focused-start request/response, session authorization, Phase 7 selection event/trace, CLI JSON, CLI text labels, report overview, subject drilldown, and objective drilldown. If new evidence arrives between render and an action, the action fails stale without writing and requires a new complete snapshot; fields from two snapshots are never merged.

## Public/private and security matrix

| Boundary | Allow | Reject / never render | Command |
|---|---|---|---|
| CLI filters | bounded week window; namespaced subject/objective; explicit cutoff/zone | raw path as identifier, unbounded/invalid window, non-finite setting | `python tests/retention_roundtrip.py` |
| Start/action request | stable bank stem/session id, displayed snapshot id, stable subject/objective, explicit action token | bank/session/output path, client cap/weight/threshold, forged override, answer/rubric/key/hidden tier/model payload | `python tests/daemon_roundtrip.py` |
| Public report/Today/session/trace | derived state, raw counts, safe provenance, component reasons | filesystem paths, answer keys, rubrics, credentials, private tiers, provider payload, raw model interaction | `python tests/phase10_uat.py` |
| Completion | explicit resolved Phase 3 heading and server-derived objectives | page view/scroll, arbitrary objective list, model proposal | `python tests/lesson_retention_roundtrip.py` |
| Override | exact confirmation, fresh snapshot, server-generated active sitting | persistent toggle, cancelled request, reused/expired session, client count/cap | `python tests/pacing_roundtrip.py` |

Security enforcement target is OWASP ASVS Level 1. No package install is planned; the repository remains stdlib-only. Large-log tests require one capture/grouping pass, not one log scan per objective. Offline/model-disabled execution must keep Today, report, evidence disclosure, lesson queue, cap, and selection available. Anki timeout/malformed/unavailable uses the locked omission sentence and never substitutes stale or zero data.

## Automated commands

Focused fast gate:

```powershell
python tests/retention_roundtrip.py
python tests/lesson_retention_roundtrip.py
python tests/selection_retention_roundtrip.py
python tests/pacing_roundtrip.py
python tests/retention_ui_roundtrip.py
python tests/phase10_uat.py
```

Required upstream regression gate:

```powershell
python tests/evidence_roundtrip.py
python tests/protocol_roundtrip.py
python tests/config_roundtrip.py
python tests/lesson_roundtrip.py
python tests/teaching_roundtrip.py
python tests/selection_roundtrip.py
python tests/day_roundtrip.py
python tests/daemon_roundtrip.py
```

Repository-wide phase gate:

```powershell
Get-ChildItem tests\*.py | Sort-Object Name | ForEach-Object { python $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
```

## Human UI gate

Plan 10-06 blocks completion until a human verifies at 1280px, 768px, and 375px:

- activity-first Today hierarchy and calm/non-gamified language;
- owner labels before counts, with itembank and Anki never summed;
- all six state names, raw evidence, uncertainty, and evidence provenance readable without relying on color;
- overview → subject → objective drilldown and selectable week windows;
- semantic trend table/text complete without chart perception;
- keyboard order, focus trap/return, Escape cancellation, status/alert semantics, and 44px narrow controls;
- exact cap, override, Anki unavailable, report failure, and chart fallback copy;
- stale snapshot refresh, explicit lesson completion, cancelled/accepted/expired override behavior;
- offline/model-disabled behavior and public DOM/API leak inspection.

## Multi-Source Coverage Audit

### GOAL — ROADMAP Phase 10 goal and success criteria

| ID | Source item | Coverage | Status |
|---|---|---|---|
| GOAL-10 | Evidence-driven retention, pacing and trends with separately labeled itembank/Anki scheduling signals. | 10-01 core, 10-03 selector, 10-04 pacing, 10-05 UI, 10-06 UAT | COVERED |
| G-01 | One shared per-render snapshot; objective due plus separate Anki due/new. | 10-01 T1/T3, 10-04 T2, 10-05 T1, 10-06 T1 | COVERED |
| G-02 | Per-subject cap through day; no Anki schedule writes. | 10-04 T1/T2, 10-05 T2, 10-06 T2 | COVERED |
| G-03 | Weak evidence raises next weight; mastered drops from ordinary rotation. | 10-01 T2, 10-03 T1, 10-06 T2 | COVERED |
| G-04 | Correct month ago without later evidence becomes at-risk. | 10-01 T2, 10-06 T2 | COVERED |
| G-05 | Weekly accuracy/hint/pending/last/risk report with every trend evidenced. | 10-01 T2/T3, 10-05 T3, 10-06 | COVERED |
| G-06 | Focused-session recommendations and optional evidence-anchored reflection, no gamification. | 10-01 T2, 10-05 T1/T3, 10-06 human gate | COVERED |

### REQ — REQUIREMENTS.md / ROADMAP IDs

All nine phase requirement IDs are covered in the requirement-to-test matrix above and appear in at least one plan's `requirements` frontmatter: SCHED-01, SCHED-02, SCHED-03, SCHED-04, TREND-01, TREND-02, TREND-03, TREND-04, TREND-05. Status: **COVERED**.

### RESEARCH — implementation features and constraints

| ID | Research item | Coverage | Status |
|---|---|---|---|
| R-01 | One pure `retention.py` beside `evidence.py`; append-only log authority and disposable derivation. | 10-01 | COVERED |
| R-02 | Capture once, derive many; immutable provenance prevents per-surface drift. | 10-01, 10-06 | COVERED |
| R-03 | Six-state conservative deterministic grammar with bounded settings. | 10-01 T2 | COVERED |
| R-04 | Pending pacing-only, latest accepted mark mastery-only, retractions disappear. | 10-01, 10-04, 10-06 | COVERED |
| R-05 | Bounded normalized weights compose with Phase 7 terms; max step; exam neutral; sole selector. | 10-03 | COVERED |
| R-06 | Per-subject local-day cap plus explicit sitting-scoped override. | 10-04 | COVERED |
| R-07 | Surface-neutral longitudinal report with CLI JSON/plain and browser twin. | 10-01, 10-05 | COVERED |
| R-08 | Anki optional read-only due/new and graceful unavailable omission. | 10-04, 10-05 | COVERED |
| R-09 | Explicit versioned lesson-completion seam; never infer page-view completion. | 10-02, 10-05 | COVERED |
| R-10 | Fixed synthetic Wave 0 fixtures and `tests/retention_roundtrip.py`. | 10-01, this validation file | COVERED |
| R-11 | Settings schema bounds and standard-library-only implementation. | 10-01; every threat model supply-chain row | COVERED |
| R-12 | Preserve existing parser/scorer/runner/evidence writer/index and Phase 4/7 seams. | all plans; 10-06 regression gate | COVERED |
| R-13 | Public/private containment, identifier-addressed routes, forged-field rejection. | 10-03 through 10-06 | COVERED |
| R-14 | Offline/model outage does not block; Anki failure is optional. | 10-04 through 10-06 | COVERED |
| R-15 | Semantic table/text is canonical; chart only optional visual summary. | 10-05 T3, 10-06 human gate | COVERED |

### CONTEXT — locked decisions

| Decision | Coverage | Status |
|---|---|---|
| D-01 one immutable snapshot per render/calculation | 10-01, 10-03, 10-04, 10-05, 10-06 | COVERED |
| D-02 disposable/reproducible append-only derivation | 10-01, 10-02, 10-03 | COVERED |
| D-03 uncertainty first-class | 10-01, 10-05, 10-06 | COVERED |
| D-04 transparent deterministic objective rules | 10-01, 10-02, 10-03, 10-05 | COVERED |
| D-05 itembank/Anki separate and unsummed | 10-04, 10-05, 10-06 | COVERED |
| D-06 six states and bounded settings | 10-01 | COVERED |
| D-07 per-subject live local-day cap | 10-04, 10-05 | COVERED |
| D-08 explicit sitting-scoped recorded override | 10-04, 10-05, 10-06 | COVERED |
| D-09 pending pacing-only; retractions disappear | 10-01, 10-04, 10-06 | COVERED |
| D-10 normalized map/snapshot into Phase 7 sole selector | 10-03, 10-05 | COVERED |
| D-11 bounded weak/mastered weighting and component trace | 10-01, 10-03 | COVERED |
| D-12 gradual capped changes; exam neutral | 10-01, 10-03, 10-06 | COVERED |
| D-13 weekly raw counts/hints/pending/last/risk/evidence | 10-01, 10-05 | COVERED |
| D-14 at-risk is proven success plus silence | 10-01, 10-06 | COVERED |
| D-15 overview→subject→objective plus JSON/plain twin | 10-01, 10-05 | COVERED |
| D-16 only accepted human marks enter mastery; model never does | 10-01, 10-02, 10-03, 10-06 | COVERED |
| D-17 FSRS baseline replayed from the log | 10-01 | COVERED |
| D-18 scheduler interface with FSRS default | 10-01 | COVERED |
| D-19 WaniKani stages/terminal retired/jpdb utility ordering | 10-01, 10-05 | COVERED |
| D-20 return rate is a stated-denominator ratio, never a streak | 10-04, 10-05 | COVERED |
| D-21 lesson-to-item transfer deferred with cost | 10-02 | COVERED |
| D-22 pending model suggestion never advances interval/mastery | 10-03, 10-05 | COVERED |
| D-23 pacing profiles preserved for future choice | 10-01 | COVERED |
| D-24 lesson-completion seam; no page-view inference | 10-02 | COVERED |

Deferred ideas are excluded, not gaps: Anki/card interval or ease writing, predictive/ML mastery, and curriculum auditing. No source item is missing from the plan set.
