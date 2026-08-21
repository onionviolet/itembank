---
phase: 14C
slug: source-adapter-registry
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
status: draft
nyquist_compliant: false
wave_0_complete: false
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

Task IDs fill in once PLAN.md files exist. The behavior rows below are frozen by research
and every plan task must map onto one of them.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | 01 | 0 | Wave 0 harness | — | N/A | unit | `python3 tests/source_adapters_roundtrip.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | Roster 1 PDF | — | scanned PDF returns typed `unsupported`, never silent empty text | unit/fixture | `python3 tests/source_adapters_roundtrip.py` (PDF case group) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | Roster 1 DOCX | — | footnote, endnote, header, footer, tracked-changes, comment parts each resolve to a gold locator | unit/fixture | `python3 tests/source_adapters_roundtrip.py` (DOCX case group) | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | Roster 2 PPTX | — | slide text plus notes-field flag; embedded video returns typed `unsupported` | unit/fixture | `python3 tests/source_adapters_roundtrip.py` against `fixtures/audit/pptx_fidelity_cases.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | Roster 3 web capture | T-14C-web | static HTML fixture yields a stable CSS or text-quote locator; redirect to a non-http scheme is refused | unit/fixture plus one loopback integration case | `fixtures/audit/web_capture_fidelity_cases.py` plus a `tests/`-level `http.server` redirect fixture | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | Roster 4 transcript | — | `.srt` and `.vtt` byte fixtures produce `start_ms` and `end_ms` locators | unit/fixture | `fixtures/audit/transcript_fidelity_cases.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | Roster 7 EPUB | — | spine order preserved, one fragment-anchored citation resolves, DRM-locked EPUB returns typed `unsupported` | unit/fixture | `fixtures/audit/epub_fidelity_cases.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | D-02 route shape | T-14C-auth | `POST /api/source/import` present in `API_ROUTES`, `ROUTE_CLI`, `SURFACE_PARITY`; cross-origin rejected; non-loopback write rejected | integration | new assertions inside `tests/daemon_roundtrip.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | Journal integration | T-14C-rights | one `applied` `source`-kind journal entry per import with `source_object_id` set when a raw file was linked; a rights-refused import raises `journal.rights_unknown` and leaves no orphan `applied` entry | integration | `tests/source_adapters_roundtrip.py` link-then-import case, or an extension of `tests/operations_roundtrip.py` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | Zip and XML hardening | T-14C-zipbomb | an oversized zip part is refused with `source.oversized` rather than hanging | unit/fixture | one adversarial case in a shared zip-format fixture module | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | Two-file atomic write | — | a fault between the Markdown write and the sidecar write leaves the prior valid pair or the new valid pair, never a half pair | fault injection | extend `tests/file_fault_tracer.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/source_adapters_roundtrip.py` — new file covering roster items 1, 2, 4, and 7 extraction fidelity plus the journal-integration cases
- [ ] `fixtures/audit/pptx_fidelity_cases.py` — new gold-case file, same `CASE_TABLE` builder shape as the existing PDF and DOCX file
- [ ] `fixtures/audit/epub_fidelity_cases.py` — new gold-case file
- [ ] `fixtures/audit/web_capture_fidelity_cases.py` — new gold-case file, static HTML only; the redirect-hardening case is a separate loopback-server test, not a fixture-file case
- [ ] `fixtures/audit/transcript_fidelity_cases.py` — new gold-case file
- [ ] New assertions inside `tests/daemon_roundtrip.py` for the new route's presence and its authority gate
- [ ] Framework install: none needed. The bespoke `*_roundtrip.py` convention already covers this phase.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live remote fetch against a real URL | Roster 3 | The degrade-never-block rule forbids a test suite that needs network. Fixtures cover the parsing; only the real fetch path is manual. | Start the daemon, `POST /api/source/import` with a known-good article URL, confirm a snapshot lands on disk, the fingerprint matches the snapshot bytes, and the journal entry records `origin` and `captured_at`. |
| OCR adapter against a photographed page | Roster 6 | Needs a running local Ollama vision model, which is not present in CI. | Run the existing `ocr` skill through the adapter wrapper on one photographed textbook page, confirm the Markdown is non-empty and the sidecar honestly records the degraded locator, since `scripts/ocr_lib.py` returns flat text with no bounding box or confidence. |
| ASR adapter | Roster 5 | Needs whisper.cpp or a hosted call; the 7900 XTX build does not exist. | Deferred with the roster item. Verify by hand when the adapter lands. |
| Package legitimacy sign-off | D-01 dependency adoption | The research pass flagged all 8 audited packages `SUS` for `unknown-downloads`, a checker telemetry gap rather than a risk signal. A human closes this. | One batched review against `SUPPLY-CHAIN-POLICY.md` section 3 before any dependency is pinned. |

---

## Validation Sign-Off

- [ ] All tasks have an `<automated>` verify or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without an automated verify
- [ ] Wave 0 covers every MISSING reference above
- [ ] No watch-mode flags
- [ ] Feedback latency under 30 seconds
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
