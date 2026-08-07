---
phase: 01
slug: evidence-spine-protocol-foundation
status: verified
threats_open: 0
asvs_level: 1
created: 2026-08-07
---

# Phase 01 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `_evidence/*.jsonl` append-only log | Local filesystem, single writer per lock | Session responses, marks, retractions, day ticks — never leaves disk |
| Question bank markdown (`.md`) | Local filesystem, human/agent-edited | Item text, keys, rationale — read by model/runtime/surfaces |
| Loopback HTTP (quiz/day surfaces) | `localhost`-only `http.server` | Learner responses in, public (keyless) item payload out |
| CI runner (`schema_validate.py` in `.github/workflows/ci.yml`) | GitHub Actions checkout | Fixture bank content only, operates under `/tmp` |
| Legacy migration input (`migrate.py --legacy-dir`) | Local filesystem, user-supplied path | Pre-existing attempt files and session data being imported |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-1-01 | Denial of Service | `evidence.iter_raw` / `events` / index rebuild / renders (carried across 01-01, 07, 08, 09, 11) | medium | mitigate | Per-line try/except records malformed lines as `warn <file>:<line> malformed, skipped`; no `sys.exit` in any reader | closed |
| T-1-02 | Tampering | `evidence.append_line` / `append_line_checked` (carried 01-01, 01-07, 01-11) | high | mitigate | Single `os.write(fd, payload)` guarded by `msvcrt.locking`/`fcntl.flock`, held across dedupe-check-then-write | closed |
| T-1-03 | Tampering / Information Disclosure | `migrate.py --legacy-dir` | high | mitigate | `scan_legacy` resolves via `os.path.abspath` and raises `MigrationScopeError` unless resolved path is inside `--base` | closed |
| T-1-04 | Information Disclosure | `_evidence/` location; CI checkout | high | mitigate | `.gitignore` excludes `_evidence/`; CI operates entirely under `/tmp`, never the checkout | closed |
| T-1-05 | Tampering / Spoofing | hashlib/sha256 usage (content_fingerprint, dedupe_key, idempotency_canon) | low | accept | Documented as integrity/change-detection only, "never as a security boundary" (evidence.py:17, model.py:155) | closed |
| T-1-06 | Information Disclosure | `bank` field in evidence/session payloads | medium | mitigate | `os.path.basename(bank_path)` — full filesystem paths never recorded | closed |
| T-1-07 | Denial of Service | `model.lint` on hostile content, `lint --json` | medium | mitigate | `json.dumps(..., ensure_ascii=False, indent=2)` — no unbounded recursion/eval path | closed |
| T-1-08 | Spoofing | Unstable/undeclared lint codes | medium | mitigate | `LINT_CODES` is a declared, sorted tuple; `test_lint_codes_declared` asserts membership | closed |
| T-1-09 | Tampering | `cmd_id_assign` bank rewrite | high | mitigate | tmp-file write then `os.replace(tmp, path)` | closed |
| T-1-10 | Tampering | Line-ending rewrite on Windows | medium | mitigate | Read and write both use `newline=""` | closed |
| T-1-11 | Repudiation | `lint` silently mutating a bank | medium | mitigate | `model.lint()` contains no write call (AST-verified); `test_identity_survives_edit` asserts `[ID:]` unchanged | closed |
| T-1-12 | Tampering | `upgrade_session` on hand-edited/future session | medium | mitigate | Distinct named errors for no-upgrade-path and newer-than-understood schema | closed |
| T-1-13 | Spoofing | Schema documents drifting from code | high | mitigate | `test_schema_versions_present`, `test_event_schema_fields` | closed |
| T-1-14 | Spoofing | Validator silently ignoring unimplemented keyword | high | mitigate | `SchemaError` raised before any instance is checked | closed |
| T-1-15 | Tampering | CI step failure swallowed | high | mitigate | `set -e` in CI step; all `schema_validate.py` invocations are bare (non-suppressed) | closed |
| T-1-16 | Tampering | bool validating as integer | medium | mitigate | `bool` explicitly excluded from `integer`/`number` type checks | closed |
| T-1-17 | Repudiation | Retraction without a reason | medium | mitigate | `retraction_event` raises on empty `reason` | closed |
| T-1-18 | Tampering | Undo implemented as deletion | high | mitigate | `retracted_ids`/`live_events` filter over an unmodified append-only log | closed |
| T-1-19 | Tampering | SQL built from CLI filter values | high | mitigate | All `sqlite3` calls use parameterized `execute(sql, params)` or static DDL | closed |
| T-1-20 | Tampering | Stale/corrupt index answering a query | high | mitigate | `index_stale`/`ensure_index` version/size/mtime-based rebuild | closed |
| T-1-21 | Repudiation | Query writing to system of record | medium | mitigate | `test_index_is_disposable` asserts log byte-identity across query/rebuild/corruption | closed |
| T-1-22 | Tampering | Whole-file writes (`cmd_render --out`, attempt files, daily_log.md) | high | mitigate | tmp-file then `os.replace` at all three call sites | closed |
| T-1-23 | Repudiation | Mark mutating the response it marks | medium | mitigate | Response events read-only; `review_state` computed at read time | closed |
| T-1-24 | Spoofing | Model verdict recorded as accepted human evidence | high | mitigate | `mark_event` raises unless `marker == "human"` | closed |
| T-1-25 | Tampering | `elapsed_ms` from the page | medium | mitigate | Server accepts only non-bool int, else None; client computes via monotonic clock, clamped ≥0 | closed |
| T-1-26 | Information Disclosure | Graded page holding an answer key | high | mitigate | Denylist test confirms key/explain/correct/opts/cats/da/why/model absent from served payload | closed |
| T-1-27 | Tampering | Lane name/date from day POST route | medium | mitigate | `day_tick_event` raises unless `date` is a real calendar date | closed |
| T-1-28 | Repudiation | Silent fallback to pre-migration tick reader | medium | mitigate | Fallback path prints notice naming `itembank migrate` | closed |
| T-1-29 | Spoofing | Positional resolution attaching wrong item during migration | high | mitigate | No similarity/fuzzy matching present; resolution is opt-in and tagged in `source_ref.resolution` | closed |
| T-1-30 | Repudiation | Migration reporting success while a record went missing | high | mitigate | Count mismatch between found/accounted exits non-zero with an error | closed |
| T-1-SC | Tampering (supply chain) | npm/pip/cargo installs (carried across all 11 plans) | low | accept | No third-party packages installed anywhere in this phase; `sqlite3` ships with CPython | closed |

*Status: open · closed · open — below {block_on} threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-1 | T-1-05 | hashlib/sha256 fingerprints (content_fingerprint, dedupe_key, idempotency_canon) are integrity/change-detection aids for a single local user, not an adversarial-input security boundary | Weibao (phase 01 plan authors) | 2026-08-07 |
| R-2 | T-1-SC | Stdlib-only constraint means no third-party package supply chain exists in this phase | Weibao (phase 01 plan authors) | 2026-08-07 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-07 | 54 | 54 | 0 | gsd-secure-phase (L1 short-circuit: register_authored_at_plan_time=true, asvs_level=1, threats_open=0) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-07
