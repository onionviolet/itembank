---
phase: 14C
slug: source-adapter-registry
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-21
---

# Phase 14C — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `14C-RESEARCH.md` section "Validation Architecture".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Bespoke `tests/*_roundtrip.py` scripts, direct `python3` execution. No pytest, no unittest runner. Confirmed by the existing `tests/identity_roundtrip.py`, `tests/journal_roundtrip.py`, `tests/operations_roundtrip.py`, `tests/file_fault_tracer.py`. |
| **Config file** | none, and none is added by this phase |
| **Quick run command** | `python3 tests/source_adapters_roundtrip.py` |
| **Full suite command** | `for t in tests/*.py; do python3 "$t" || exit 1; done` |
| **Estimated runtime** | ~30 seconds quick, ~3 minutes full (extrapolated from the 14A freeze record, not measured this session) |

---

## Sampling Rate

- **After every task commit:** Run `python3 tests/source_adapters_roundtrip.py`
- **After every plan wave:** Run `for t in tests/*.py; do python3 "$t" || exit 1; done`
- **Before `/gsd-verify-work`:** Full suite green, plus `python3 itembank.py guard .` clean
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

Task IDs filled in 2026-08-28 by plan `14C-08` Task 3 from the eight plans' own
task names. Every behavior row below was frozen by research before execution;
every one now names the plan task that covers it and the `check_*` function
that proves it. `nyquist_compliant` is `true` because every row has an
automated verify: no row rests on a manual checkpoint alone. The two
manual-only verifications below are additive to the automated rows, not
substitutes for them, and their run state is recorded honestly.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01 T3 thin slice | 01 | 0 | Wave 0 harness | — | one PDF imports as a cited source through one boundary | unit | `python3 tests/source_adapters_roundtrip.py` (`check_thin_slice`) | ✅ | ✅ green |
| 02 T3 PDF locators | 02 | 2 | Roster 1 PDF | — | scanned PDF returns typed `unsupported`, never silent empty text | unit/fixture | `python3 tests/source_adapters_roundtrip.py` (`check_pdf_gold_cases`, `check_scanned_pdf_is_typed_unsupported`) | ✅ | ✅ green |
| 02 T2 DOCX adapter | 02 | 2 | Roster 1 DOCX | — | footnote, endnote, header, footer, tracked-changes, comment parts each resolve to a gold locator | unit/fixture | `python3 tests/source_adapters_roundtrip.py` (`check_docx_gold_cases`, `check_docx_extra_parts`) | ✅ | ✅ green |
| 03 T2 PPTX adapter | 03 | 3 | Roster 2 PPTX | — | slide text plus notes-field flag; a media-only slide returns typed `unsupported` per slide | unit/fixture | `python3 tests/source_adapters_roundtrip.py` (`check_pptx_gold_cases`, `check_pptx_notes_flag`, `check_pptx_partial_refusal`) | ✅ | ✅ green |
| 04 T1 and T2 web capture | 04 | 4 | Roster 3 web capture | T-14C-web | static HTML yields a stable CSS and text-quote locator; a redirect to a non-http scheme is refused | unit/fixture plus loopback integration | `python3 tests/source_adapters_roundtrip.py` (`check_web_gold_cases`, `check_web_locator_anchors`, `check_redirect_hardening`) | ✅ | ✅ green |
| 05 T2 transcript adapter | 05 | 5 | Roster 4 transcript | — | `.srt` and `.vtt` byte fixtures produce `start_ms` and `end_ms` locators | unit/fixture | `python3 tests/source_adapters_roundtrip.py` (`check_transcript_gold_cases`, `check_transcript_timestamp_locators`) | ✅ | ✅ green |
| 06 T1 OCR adapter | 06 | 6 | Roster 6 OCR | — | a photographed page binds through the one path; bbox and confidence are null and the schema refuses a fabricated bbox | unit/fixture (stubbed bridge) | `python3 tests/source_adapters_roundtrip.py` (`check_ocr_stubbed_extraction`, `check_ocr_honest_degradation`) | ✅ | ✅ green |
| 08 T1 ASR registration | 08 | 8 | Roster 5 ASR | — | `adapter="asr"` is a named `source.backend_unconfigured` refusal, not `adapter_unknown`, and its locator shape is frozen and tested before any backend exists | unit | `python3 tests/source_adapters_roundtrip.py` (`check_asr_registered_not_built`, `check_asr_locator_shape_frozen`) | ✅ | ✅ green |
| 07 T3 EPUB adapter | 07 | 7 | Roster 7 EPUB | — | spine order preserved, one fragment-anchored citation resolves, DRM-locked EPUB returns typed `unsupported` | unit/fixture | `python3 tests/source_adapters_roundtrip.py` (`check_epub_spine_order`, `check_epub_fragment_anchor`, `check_epub_drm_refused`) | ✅ | ✅ green |
| 01 T4 and 04 T3 routes | 01, 04 | 1, 4 | D-02 route shape | T-14C-auth | both source routes present in `API_ROUTES`, `ROUTE_CLI`, `SURFACE_PARITY`; cross-origin rejected | integration | `python3 tests/daemon_roundtrip.py` (`check_api_route_scope`, `check_api_source_import_route`, `check_api_source_recheck_route`, `check_cross_origin_gate_on_mutating_routes`) | ✅ | ✅ green |
| 01 T3 and 04 T2 journal | 01, 04 | 1, 4 | Journal integration | T-14C-rights | one `applied` `source`-kind entry per import; a rights-refused import raises `journal.rights_unknown` and leaves no orphan sidecar | integration | `python3 tests/source_adapters_roundtrip.py` (`check_thin_slice`, `check_rights_refusal`, `check_no_rights_escalation`, `check_remote_capture_rights`) | ✅ | ✅ green |
| 02 T1 zip and XML seam | 02 | 2 | Zip and XML hardening | T-14C-zipbomb | an oversized declared zip part is refused with `source.oversized` before decompression, inside a five-second bound; a DOCTYPE or entity declaration is refused before the parser runs | unit/fixture | `python3 tests/source_adapters_roundtrip.py` (`check_zip_bomb_guard`, `check_xml_entity_guard`, `check_epub_uses_shared_seam`) | ✅ | ✅ green |
| 02 T3 two-file pair | 02 | 2 | Two-file atomic write | — | a fault between the sidecar write and the journal append leaves the prior valid pair or the new valid pair, never a half pair | fault injection | `python3 tests/file_fault_tracer.py` (`check_two_file_pair_atomicity`) | ✅ | ✅ green |
| 08 T2 vendoring gate | 08 | 8 | Supply chain | T-14C-SC, T-14C-49 | every recorded checksum is recomputed in CI and a mismatch, a missing artifact, or a row naming a parked package fails the build | integration | `python3 scripts/check_vendored.py`; `python3 tests/source_adapters_roundtrip.py` (`check_vendored_manifest`) | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/source_adapters_roundtrip.py` -- new file covering roster items 1, 2, 4, and 7 extraction fidelity plus the journal-integration cases
- [x] `fixtures/audit/pptx_fidelity_cases.py` — new gold-case file, same `CASE_TABLE` builder shape as the existing PDF and DOCX file
- [x] `fixtures/audit/epub_fidelity_cases.py` — new gold-case file
- [x] `fixtures/audit/web_capture_fidelity_cases.py` — new gold-case file, static HTML only; the redirect-hardening case is a separate loopback-server test, not a fixture-file case
- [x] `fixtures/audit/transcript_fidelity_cases.py` — new gold-case file
- [x] New assertions inside `tests/daemon_roundtrip.py` for the new route's presence and its authority gate
- [x] Framework install: none needed. The bespoke `*_roundtrip.py` convention already covers this phase.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live remote fetch against a real URL (RUN 2026-08-28 against a loopback origin, not a public one; the redirect, timeout, oversize, and 404 paths are all covered automatically against a real socket) | Roster 3 | The degrade-never-block rule forbids a test suite that needs network. Fixtures cover the parsing; only the real fetch path is manual. | Start the daemon, `POST /api/source/import` with a known-good article URL, confirm a snapshot lands on disk, the fingerprint matches the snapshot bytes, and the journal entry records `origin` and `captured_at`. |
| OCR adapter against a photographed page (UNRUN 2026-08-28: no Ollama server was reachable; recorded as unrun in 14C-06-SUMMARY.md, never as passed) | Roster 6 | Needs a running local Ollama vision model, which is not present in CI. | Run the existing `ocr` skill through the adapter wrapper on one photographed textbook page, confirm the Markdown is non-empty and the sidecar honestly records the degraded locator, since `scripts/ocr_lib.py` returns flat text with no bounding box or confidence. |
| ASR adapter | Roster 5 | Needs whisper.cpp or a hosted call; the 7900 XTX build does not exist. | Deferred with the roster item. Verify by hand when the adapter lands. |
| Package legitimacy sign-off (PASSED 2026-08-27, all six approved on per-package PyPI, GitHub, and OSV evidence; recorded as D-14C-3) | D-01 dependency adoption | The research pass flagged all 8 audited packages `SUS` for `unknown-downloads`, a checker telemetry gap rather than a risk signal. A human closes this. | One batched review against `SUPPLY-CHAIN-POLICY.md` section 3 before any dependency is pinned. |

---

## Validation Sign-Off

- [x] All tasks have an `<automated>` verify or a Wave 0 dependency
- [x] Sampling continuity: no 3 consecutive tasks without an automated verify
- [x] Wave 0 covers every MISSING reference above
- [x] No watch-mode flags
- [x] Feedback latency under 30 seconds
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** signed off 2026-08-28 by plan `14C-08` Task 3, on the evidence
recorded in `14C-FREEZE.md`. Every behavior row is green with a named check.
The one manual verification that did not run, the OCR page against a live
vision model, is recorded as unrun rather than assumed, and it is additive to
`check_ocr_stubbed_extraction` and `check_ocr_honest_degradation` rather than
the only thing covering that row.
